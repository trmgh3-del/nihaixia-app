/* ================= AI 问诊引擎（OpenAI 兼容接口） ================= */
import { store } from './store.js'
import { loadData } from './data.js'
import { resolveItem } from './routes.js'

/* 精简内核：从 SKILL.md 蒸馏的倪师思维人格（离线内置） */
export const LITE_PROMPT = `你是「倪师经方AI」，以倪海厦（美国汉唐中医诊所创办人，人纪/天纪作者）的视角与口吻讲授经方中医。你的一切回答遵循以下内核：

【身份】经方家思维：六经辨证为纲，八纲（阴阳表里虚实寒热）为目，方证对应，同症同治，不立病名。
【铁律】
1. 先辨六经再选方：太阳（脉浮头项强痛恶寒，桂枝汤/麻黄汤）、阳明（但热不寒胃家实，白虎/承气）、少阳（口苦咽干目眩往来寒热，小柴胡）、太阴（腹满吐利食不下，理中）、少阴（脉微细但欲寐，四逆/真武）、厥阴（消渴气上撞心寒热错杂，乌梅丸）。
2. 关键追问不能省：出汗？大便？小便？手脚温度？口渴？睡眠？——问诊往来之后再给方向。
3. 胃气为生死关键：眠、胃口、二便、手足温度、汗，是倪氏六大健康标准。
4. 阳药为主，经方原方最可靠；剂量注明体系（汉量一两≈15.6g；倪师临床台湾制一两=十钱、一钱≈3.75g，古方一两常换算为一钱）。
5. 温病派滋阴思路需批判看待；对西药过度治疗直言不讳，但给出依据。
【口吻】讲课式、口语化、笃定幽默；常用「诸位」「很简单嘛」「我跟你说」「对不对」「读者认为呢」；可以跑题讲故事、举例临床医案；结尾常用断言式收束（如「汗一透，烧就退了，就这么简单」）。不用学术编号结构、不用小标题清单腔。
【安全】涉及峻药（生附子/生半夏/麻黄/细辛/硫磺等）必须给完整剂量范围与煎服法并强调遵医嘱；急重症（胸痛/大出血/高热惊厥等）要求立即就医；文末附简短免责：「个人观点，仅供学习参考，用药请遵医嘱」。`

/* 最近一次 RAG 引用（供前端展示溯源） */
export const lastRagRefs = { refs: [] }

export async function buildMessages(question) {
  const cfg = store.ai
  const messages = []
  lastRagRefs.refs = []
  if (cfg.mode === 'full') {
    const raw = await loadData('skill_raw')
    messages.push({ role: 'system', content: raw.md })
  } else if (cfg.mode === 'rag') {
    let rag = ''
    try {
      const r = await buildRag(question)
      rag = r.text
      lastRagRefs.refs = r.refs
    } catch (e) { console.error(e) }
    messages.push({ role: 'system', content: LITE_PROMPT + (rag ? '\n\n【知识库检索参考】（回答时优先采用其中原文/剂量，注明出处模块）：\n' + rag : '') })
  } else {
    messages.push({ role: 'system', content: LITE_PROMPT })
  }
  // 近 12 轮上下文
  const hist = store.chats.filter(c => c.role === 'user' || c.role === 'assistant').slice(-12)
  hist.forEach(c => messages.push({ role: c.role, content: c.content }))
  messages.push({ role: 'user', content: question })
  return messages
}

/* 极简 RAG：按关键词重叠从索引挑 top 条目，加载正文 */
async function buildRag(q) {
  const idx = await loadData('index')
  const chars = [...new Set(q.split('').filter(c => /[\u4e00-\u9fa5A-Za-z]/.test(c)))]
  const scored = []
  for (const e of idx) {
    let s = 0
    const hay = e.t + ' ' + e.s
    for (const c of chars) if (hay.includes(c)) s++
    if (e.t.includes(q)) s += 20
    if (s > 3) scored.push({ e, s: s / Math.sqrt(hay.length) })
  }
  scored.sort((a, b) => b.s - a.s)
  const top = scored.slice(0, 3)
  const parts = []
  const refs = []
  for (const { e } of top) {
    try {
      const item = await resolveItem(e)
      if (item && (item.b || item.原文 || item.clinical)) {
        const body = item.b || `【原文】${item.原文 || ''}\n【性味】${item.性味 || ''}\n【主治】${item.主治 || ''}\n【倪注】${item.倪注 || ''}${item.clinical ? '\n【临床】' + item.clinical : ''}`
        parts.push(`◆ ${e.t}（${e.f}）\n${String(body).slice(0, 2600)}`)
        refs.push({ f: item.f || e.f, i: item.id || e.i, t: String(item.t || e.t).replace(/^Q: /, ''), c: item.cat || e.c })
      }
    } catch (err) { /* skip */ }
  }
  return { text: parts.join('\n\n---\n\n'), refs }
}

/* 发起对话；onDelta 流式回调；返回完整文本 */
export async function chatCompletion(question, onDelta) {
  const cfg = store.ai
  if (!cfg.apiKey) throw new Error('未配置 API Key')
  const messages = await buildMessages(question)
  const url = cfg.baseUrl.replace(/\/+$/, '') + '/chat/completions'
  const body = { model: cfg.model, messages, temperature: Number(cfg.temperature) || 0.7, stream: !!cfg.stream }
  if (!cfg.stream) {
    const res = await postJson(url, cfg.apiKey, body)
    const text = res && res.choices && res.choices[0] && res.choices[0].message ? res.choices[0].message.content : ''
    onDelta && onDelta(text, true)
    return text
  }
  // 流式
  return await new Promise((resolve, reject) => {
    let full = ''
    let buf = ''
    const task = uni.request({
      url,
      method: 'POST',
      timeout: 180000,
      header: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + cfg.apiKey },
      data: body,
      enableChunked: true,
      responseType: 'text',
      success: () => {},
      fail: err => reject(new Error(err && err.errMsg || '请求失败')),
      onChunkReceived: res => {
        try {
          const bytes = res.data
          let text = ''
          if (typeof bytes === 'string') text = bytes
          else if (bytes && bytes.__proto__ && bytes.__proto__.constructor.name === 'ArrayBuffer') text = ab2str(bytes)
          else if (bytes instanceof ArrayBuffer) text = ab2str(bytes)
          else text = String(bytes)
          buf += text
          const lines = buf.split('\n')
          buf = lines.pop() || ''
          for (const ln of lines) {
            const s = ln.trim()
            if (!s.startsWith('data:')) continue
            const payload = s.slice(5).trim()
            if (payload === '[DONE]') continue
            try {
              const j = JSON.parse(payload)
              const d = j.choices && j.choices[0] && j.choices[0].delta
              if (d && d.content) { full += d.content; onDelta && onDelta(d.content, false) }
            } catch (e) { /* 半包忽略 */ }
          }
        } catch (e) { console.error(e) }
      },
      complete: () => {
        if (!full) {
          // 某些平台 onChunkReceived 不可用 -> 静默重试非流式
          postJson(url, cfg.apiKey, { ...body, stream: false }).then(res => {
            const text = res && res.choices && res.choices[0] && res.choices[0].message ? res.choices[0].message.content : ''
            onDelta && onDelta(text, true)
            resolve(text)
          }).catch(reject)
          return
        }
        resolve(full)
      }
    })
    if (globalThis.__lastReq) { try { globalThis.__lastReq.abort() } catch (e) { /* noop */ } }
    globalThis.__lastReq = task
  })
}

function ab2str(buffer) {
  const arr = new Uint8Array(buffer)
  let s = ''
  const CH = 8192
  for (let i = 0; i < arr.length; i += CH) {
    s += String.fromCharCode.apply(null, arr.subarray(i, i + CH))
  }
  return decodeURIComponent(escape(s))
}

function postJson(url, key, body) {
  return new Promise((resolve, reject) => {
    uni.request({
      url, method: 'POST', timeout: 180000,
      header: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + key },
      data: body,
      success: res => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data)
        else reject(new Error('HTTP ' + res.statusCode + ' ' + (res.data && res.data.error && res.data.error.message ? res.data.error.message : '')))
      },
      fail: err => reject(new Error(err && err.errMsg || '网络失败'))
    })
  })
}

export const QUICK_PROMPTS = [
  '感冒发烧、怕冷、无汗、肌肉酸痛，怎么辨证用什么方？',
  '失眠多梦、心烦、手脚温，倪师怎么治失眠？',
  '长期便秘，倪师的思路是什么？用大承气还是别的？',
  '口苦、咽干、往来寒热、胸胁胀满，开什么方？给剂量',
  '手脚冰凉、但欲寐、脉微细，是哪一经？怎么治？',
  '倪师讲牛奶到底能不能喝？为什么？',
  '黄芪桂枝五物汤和桂枝汤的区别？',
  '给讲一个倪师治癌症的真实医案'
]
