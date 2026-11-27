# PriceBell (น้องเฝ้าพอร์ต) — บันทึกการวางแผน

สรุปสิ่งที่คุยและตัดสินใจกันไว้ถึงวันที่ 26 พ.ย. 2026 เอกสารแผนฉบับเต็มอยู่ที่
[PriceBell — แผนโปรเจกต์](https://claude.ai/artifact/DrWsjdXZMsgQEYR87azYCM)

> สถานะ: ขั้น 0 และขั้น 1 ของ MVP เสร็จแล้ว (บอทตอบ `/start` ได้จริง) ต่อไปคือขั้น 2 (§9.2)

---

## 1. การตัดสินใจที่ทำไปแล้ว

| เรื่อง | ตัดสินใจ | เหตุผล |
|---|---|---|
| ชื่อโปรเจกต์ | **PriceBell** (ชื่อไทย "น้องเฝ้าพอร์ต") | ตัดสินใจ 25 พ.ย. 2026 |
| Telegram library | **python-telegram-bot** (ไม่ใช่ aiogram) | เรียนง่ายกว่าสำหรับคนที่ยังไม่เคยใช้ทั้งสองตัว: เอกสารภาษาอังกฤษครบ ตัวอย่างและคำตอบในเน็ตเยอะ library อยู่แค่ใน adapter และ handler เท่านั้น ส่วน engine ไม่ import |
| แพลตฟอร์มแรก | **Telegram** (ไม่ใช่ LINE) | คนสัมภาษณ์ทั้งไทยและต่างประเทศลองได้ทันทีผ่าน `t.me/...`, ไม่มีโควตาส่งข้อความรายเดือน, setup เร็ว, dev ด้วย long polling ได้ |
| LINE | เก็บไว้เป็น adapter ตัวที่สองใน v3 | พิสูจน์ว่าแกนกลางไม่ผูกกับแพลตฟอร์ม |
| กลุ่มผู้ใช้ | โปรเจกต์ทำเล่น ใช้เองและเพื่อน | ไม่ต้องออกแบบรองรับผู้ใช้จำนวนมาก |
| เป้าหมายสัมภาษณ์ | บริษัทไทยหรือต่างประเทศก็ได้ | README และ diagram เป็นภาษาอังกฤษ, บอทรองรับสองภาษา |
| ตัดออกจากแผน | TimescaleDB, React dashboard | ข้อมูลน้อยมาก ไม่ต้องเก็บ tick, ใส่ไปจะดู over-engineer |
| เพิ่มเข้าแผน | คำสั่ง `/demo`, ช่วงห้ามรบกวน, บอกเวลาและความล่าช้าของราคา | คนสัมภาษณ์เห็น flow ครบโดยไม่ต้องรอตลาดขยับ, ตลาด US เปิดกลางคืนเวลาไทย |
| หลัก UX | ทุกอย่างทำได้ด้วยการกด 1–3 ครั้ง พิมพ์เป็นทางสำรอง | เป้าหมาย "ใช้ง่าย" |
| Layout ของโค้ด | `src/pricebell/` แบ่งตาม layer (รายละเอียด §6.1) | `src/` ทำให้เทสต์ใช้แพ็กเกจแบบเดียวกับตอน deploy, แบ่งตาม layer ทำให้เห็นจากต้นไม้ไฟล์ว่า engine ไม่รู้จัก Telegram (ตัดสินใจ 25 พ.ย. 2026) |
| `Messenger` รับอะไร | ข้อความกลาง `OutgoingMessage` (text + ปุ่มแบบ action + id) adapter แปลงเป็นของแพลตฟอร์มเอง | logic เลือกข้อความและปุ่มอยู่ที่เดียว, LINE adapter ไม่ต้องเขียนซ้ำ, `callback_data` อยู่ใน adapter Telegram เท่านั้น (ตัดสินใจ 25 พ.ย. 2026) |
| ภาษาเริ่มต้นของบอท | **ไทย** ตอบอังกฤษเฉพาะเมื่อ `language_code` ขึ้นต้นด้วย `en` | ผู้ใช้หลักเป็นคนไทย, ไม่มี `language_code` หรือเป็นภาษาอื่นก็ตอบไทย, ใช้ `startswith("en")` เพื่อให้ `en-US` และ `en-GB` ได้อังกฤษด้วย (ตัดสินใจ 26 พ.ย. 2026) |

---

## 2. ไอเดียตั้งต้น (ก่อนรีวิว)

- LINE bot แจ้งเตือนราคา: หุ้นไทย (PTT.BK, CPALL.BK), หุ้น US (AAPL, NVDA), ETF (SPY, QQQ, VOO, GLD), ทอง (GC=F), น้ำมัน (CL=F, BZ=F), ค่าเงิน (THB=X)
- ฟีเจอร์: watchlist, คำสั่งแชท, alert ราคาเป้า / % ในวัน / 52 สัปดาห์ / SMA50/200 / RSI, สรุปตลาดรายวัน, disclaimer ทุกข้อความ
- Stack: FastAPI + SQLAlchemy + PostgreSQL, APScheduler, yfinance ผ่าน provider adapter, Docker
- จุดออกแบบ: เวลาตลาด, ดึงข้อมูลครั้งเดียวต่อ symbol + cache, กันแจ้งเตือนซ้ำ, idempotent jobs, UTC, ตรวจ signature, เทสต์ด้วย backtest

---

## 3. ผลรีวิวแผนเดิม (จุดอ่อนที่เจอ)

1. **Free tier host จะ sleep:** Render free จะ sleep เมื่อไม่มี traffic ราว 15 นาที ทำให้ scheduler หยุดและ alert ไม่ยิง → ใช้ instance ที่เปิดตลอด (Fly.io หรือ Railway) ส่วน DB ใช้ Neon หรือ Supabase
2. **yfinance ไม่ได้เร็ว:** เป็น API ไม่เป็นทางการ โดน 429 หรือบล็อกจาก IP ของ cloud ได้ หุ้นไทยล่าช้า ~15 นาที → ใช้ cache, ดึงแบบ batch, ไม่ poll ตลาดปิด, บอกความล่าช้าตรงๆ, v2 ใช้ Finnhub WebSocket สำหรับหุ้น US
3. **โควตา push ของ LINE น้อย:** หลักร้อยข้อความต่อเดือน (ข้อนี้หายไปเมื่อเปลี่ยนเป็น Telegram)
4. **พึ่งการพิมพ์มากเกินไป:** ผู้ใช้มือถือไม่พิมพ์คำสั่งให้ถูก syntax → ใช้ปุ่ม
5. **`ลบ 2` เสี่ยงลบผิดตัว:** ลำดับในรายการเปลี่ยนได้ → ปุ่มต้องอ้างด้วย id
6. **ขาดราคาทองแบบที่คนไทยใช้ (บาทละ 96.5%):** GC=F เป็น USD/ออนซ์
7. **ขอบเขตใหญ่เกินไปสำหรับโปรเจกต์ที่ต้องทำเสร็จ**
8. **ภาษาของ alert จาก indicator:** ต้องเป็นข้อเท็จจริง ("RSI ต่ำกว่า 30") ไม่ใช่ "สัญญาณซื้อ"

---

## 4. เทียบ Telegram กับ LINE

| เรื่อง | Telegram | LINE |
|---|---|---|
| โควตา | ไม่มีโควตารายเดือน, มี rate limit (~1 ข้อความ/วินาทีต่อแชท, ~30/วินาทีรวม) | push ฟรีหลักร้อยต่อเดือน |
| คนสัมภาษณ์ต่างประเทศ | ลองได้ทันที | ส่วนใหญ่ไม่มี LINE |
| แก้ข้อความเดิม | ได้ (`editMessageText`) | ไม่ได้ |
| ข้อมูลที่ปุ่มส่งกลับ | `callback_data` ≤ 64 bytes | postback ≤ 300 ตัวอักษร |
| การ์ด | text HTML/Markdown + ปุ่ม หรือรูป | Flex Message |
| ช่วงห้ามรบกวน | ส่งแบบเงียบได้ (`disable_notification`) | ต้องเก็บไว้ส่งทีหลัง |
| Webhook security | `X-Telegram-Bot-Api-Secret-Token` | HMAC-SHA256 ของ body |
| ตอน dev | long polling ได้ | ต้องมี HTTPS (ngrok) |
| ผู้ใช้ในไทย | กลุ่มเทรดเดอร์/คริปโต | แทบทุกคน |
| Web app ในแชท | Mini Apps | LIFF |

ตัวเลขโควตาและ rate limit เป็นค่าประมาณ ต้องเช็คเอกสารทางการก่อนเริ่ม

---

## 5. UX (เวอร์ชัน Telegram)

**เมนูถาวร (Reply Keyboard 2×3):** พอร์ตของฉัน · เช็คราคา · ตั้งแจ้งเตือน · แจ้งเตือนของฉัน · ตั้งค่า · วิธีใช้

**คำสั่ง (สองภาษา เลือกภาษาที่ตอบจาก `language_code`)**

| คำสั่ง | แบบไทย | ทำอะไร |
|---|---|---|
| `/price NVDA` | `ราคา NVDA` หรือ `NVDA` เฉยๆ | การ์ดราคา + % วันนี้ + ราคาเป็นบาท |
| `/alert NVDA < 120` | `แจ้งเตือน NVDA < 120` | ตั้ง alert แบบพิมพ์เอง |
| `/alerts` | `รายการแจ้งเตือน` | รายการ alert พร้อมปุ่มหยุด/ลบ |
| `/watch AAPL` | `เพิ่ม AAPL` | เพิ่มเข้าพอร์ต |
| `/portfolio` | `พอร์ต` | ราคาทุกตัวในพอร์ต |
| `/settings` | `ตั้งค่า` | ช่วงห้ามรบกวน, หยุดแจ้งเตือนชั่วคราว |
| `/demo` | — | ยิง alert จำลองภายใน 10 วินาที |

**Flow ตั้ง alert ด้วยปุ่ม (แก้ข้อความเดิมทุกขั้น)**

1. กด "ตั้งแจ้งเตือน" → เลือกหุ้นจากพอร์ต หรือ "พิมพ์ชื่ออื่น"
2. เลือกเงื่อนไข: ลง 3% · ลง 5% · ขึ้น 3% · ขึ้น 5% · แกว่งวันละ ±3% · กำหนดราคาเอง
3. บอทแปลง % เป็นราคาเป้าให้เห็น (เช่น NVDA ≤ 147.61, −5% จาก 155.38) พร้อมปุ่ม "เลิกทำ" แทนการถามยืนยัน
4. "กำหนดราคาเอง" ใช้ `ForceReply` ให้ผู้ใช้พิมพ์แค่ตัวเลข

**หลักการอื่น**

- ปุ่มใต้ข้อความเดาขั้นถัดไป เช่น การ์ดราคามี [รีเฟรช] [แจ้งถ้าลง 5%] [เพิ่มเข้าพอร์ต] ส่วน alert ที่เด้งมี [ตั้งต่อที่ −5%] [ปิดแจ้งเตือนนี้] [เงียบถึงพรุ่งนี้]
- ปุ่มเปลี่ยนตามสถานะ เช่น ถ้าอยู่ในพอร์ตแล้วโชว์ "เอาออก" แทน "เพิ่ม"
- ปุ่มอ้างด้วย id (เช่น `ad:42`) กดในข้อความเก่าได้อย่างปลอดภัย ถ้า alert ถูกลบไปแล้วให้ตอบว่า "รายการนี้ถูกลบไปแล้ว"
- ช่วงห้ามรบกวน (ค่าเริ่มต้น 23:00–07:00 เวลาไทย) ส่งแบบไม่มีเสียง
- รองรับ inline mode (`@bot NVDA` ในแชทอื่น) ไว้ใน v2 ได้

**ดีไซน์ฝั่ง LINE ที่คุยไว้ (เก็บไว้ใช้ตอนทำ LINE adapter)**

- Rich Menu ขนาดใหญ่ 2500×1686 จำนวน 6 ปุ่ม ปุ่มที่ใช้บ่อยอยู่แถวบน
- Quick Reply หายเมื่อมีข้อความใหม่ จึงต้องให้ทุกฟีเจอร์หลักเข้าได้จาก Rich Menu เสมอ
- postback ใช้ `displayText` (สิ่งที่กดขึ้นเป็นข้อความในแชท) และ `inputOption=openKeyboard` + `fillInText` (เติมคำสั่งให้ ไม่ต้องเก็บ state บทสนทนา)
- คำสั่งตอบด้วย reply (ไม่เสียโควตา) มีแค่ alert ที่ใช้ push และรวมเป็น push เดียวต่อ user ต่อรอบ
- quick reply ได้สูงสุด 13 ปุ่ม, label ≤ 20 ตัวอักษร, การ์ดใช้ Flex Message

---

## 6. สถาปัตยกรรม

แอปเดียว (FastAPI) มีสองทางเข้า คือ update จาก Telegram และ scheduler ทุก 60 วินาที ทั้งสองทางใช้ provider และ Postgres ร่วมกัน

```
Telegram ⇄ Bot adapter ⇄ Command handlers ─┐
   ▲      (secret token,   (คำสั่ง + ปุ่ม,   ├─► Provider + cache ─► yfinance / Finnhub
   │       กัน update ซ้ำ)  แก้ข้อความเดิม)    │    (TTL, single-flight;   (batch ต่อ symbol)
   │                                        │     ใช้ร่วมกันทั้งแชทและ alert)
Send queue ◄── Alert engine ───────────────┘
(token bucket,  (ทุก 60 วิ, pure rules,
 retry 429)      outbox: AlertEvent)
      │              │
      └──────┬───────┘
             ▼
Postgres: users · watchlist · alerts · alert_events · processed_updates
```

**Stack**

- Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL (ใช้ SQLite in-memory ตอนเทสต์)
- APScheduler (job เดียว, `max_instances=1`)
- python-telegram-bot (ไม่ใช้ JobQueue และ `AIORateLimiter` ของมัน เพราะ scheduler และ send queue เป็นของเราเอง)
- yfinance ใน MVP, Finnhub ใน v2
- Docker, Fly.io หรือ Railway, Neon หรือ Supabase
- pytest + ruff, GitHub Actions ใน v3

**Data model**

| ตาราง | เก็บอะไร |
|---|---|
| users | Telegram user id, ภาษา, ช่วงห้ามรบกวน, หยุดแจ้งเตือนถึงเมื่อไหร่ |
| watchlist_items | user + symbol |
| alerts | symbol, ชนิด, threshold, state (armed, generation, ยิงล่าสุดเมื่อไหร่, session ที่ยิงล่าสุด) |
| alert_events | การยิงแต่ละครั้ง, dedupe key, สถานะส่ง (outbox) |
| processed_updates | `update_id` ที่ประมวลผลแล้ว |

### 6.1 Layout ของโค้ด

ตัดสินใจ 25 พ.ย. 2026 ต้นไม้นี้คือเป้าหมาย ไม่ต้องสร้างทั้งหมดตั้งแต่แรก ให้สร้างโฟลเดอร์ตอนที่ slice ไหนต้องใช้ (หลักเดียวกับตาราง DB) ขั้น 0 มีแค่ `pyproject.toml`, `settings.py` และเทสต์หนึ่งตัว

```
pricebell/
├── pyproject.toml
├── .env.example
├── src/pricebell/
│   ├── main.py            # composition root: ประกอบทุกชิ้นเข้าด้วยกัน
│   ├── settings.py        # ที่เดียวที่อ่าน os.environ
│   ├── domain/            # pure ล้วน ไม่ import อะไรนอก stdlib
│   │   ├── prices.py      #   PriceSnapshot (Decimal)
│   │   ├── symbols.py     #   ตาราง alias + normalise
│   │   └── rules.py       #   alert rules (ขั้น 5)
│   ├── ports.py           # PriceProvider, Messenger (typing.Protocol), OutgoingMessage
│   ├── services/          # use case + transaction boundary
│   │   ├── watchlist.py
│   │   └── alert_engine.py
│   ├── messages.py        # ข้อความ th/en + disclaimer + บรรทัดเวลาของราคา (ของกลาง)
│   ├── providers/         # yahoo.py, cache.py (TTL + single-flight)
│   ├── db/                # models.py, session.py
│   ├── bot/               # ทุกอย่างที่รู้จัก Telegram อยู่ในนี้เท่านั้น
│   │   ├── app.py         #   สร้าง Application + register handler
│   │   ├── handlers/      #   start.py, price.py, watchlist.py, alerts.py
│   │   ├── callbacks.py   #   encode/decode callback_data (≤ 64 bytes)
│   │   ├── keyboards.py
│   │   └── messenger.py   #   TelegramMessenger implements Messenger
│   └── queue/             # send queue (ขั้น 8)
└── tests/
    ├── fakes.py           # FakePriceProvider, FakeMessenger
    ├── unit/
    └── integration/
```

**`src/` layout:** ถ้าไม่มี `src/` pytest จะ import โค้ดจากโฟลเดอร์ตรงๆ เทสต์จึงผ่านได้ทั้งที่แพ็กเกจที่ติดตั้งจริงอาจพัง ต้องตั้งค่าเพิ่มคือ `pip install -e .` หรือ `pythonpath = ["src"]` ในส่วน pytest ของ `pyproject.toml`

**กฎการ import:** dependency ชี้เข้าข้างในทางเดียว

- `domain` ไม่ import ใคร
- `services` import ได้แค่ `domain`, `ports` และ `messages`
- `bot/`, `providers/`, `db/` และ `queue/` คือ adapter ที่อยู่วงนอก
- มีแค่ `main.py` ที่รู้จักคลาสจริงทุกตัวและเป็นคนประกอบ ส่วนที่เหลือคุยกันผ่าน interface
- v3: เพิ่ม `line/` ข้างๆ `bot/` แล้วแก้แค่ `main.py` ไม่แตะ `services/` หรือ `domain/` ถ้าอยากให้เครื่องบังคับกฎนี้ ใส่ `import-linter` ใน CI ได้ตอน v3

**`Messenger` รับข้อความกลาง (`OutgoingMessage`):** engine สร้าง text และรายการปุ่มแบบ action + id (เช่น "ตั้งต่อที่ −5%" อ้าง alert 42) โดยไม่รู้ว่าจะไปแพลตฟอร์มไหน `TelegramMessenger` แปลงเป็น InlineKeyboard และ `callback_data` เอง ส่วน LINE adapter แปลงเป็น Flex Message ของมันเอง ทางเลือกที่ไม่เลือกคือให้ engine ส่งแค่ `AlertEvent` แล้วให้ adapter จัดรูปข้อความเอง ซึ่งจะทำให้ทุก adapter ต้องเขียน logic เลือกข้อความและปุ่มซ้ำกัน

---

## 7. สินทรัพย์และแหล่งข้อมูล

| กลุ่ม | symbol (Yahoo) | พิมพ์แบบย่อได้ | ความสดใน MVP |
|---|---|---|---|
| หุ้นไทย | PTT.BK, CPALL.BK | PTT, CPALL | ล่าช้า ~15 นาที |
| หุ้น US | AAPL, NVDA | — | ใกล้เคียง real-time (v2: Finnhub WS) |
| ETF | SPY, QQQ, VOO, GLD | — | เหมือนหุ้น US |
| ทองคำโลก | GC=F | ทอง | futures เกือบ 24 ชม. |
| น้ำมัน | CL=F, BZ=F | น้ำมัน, เบรนท์ | futures เกือบ 24 ชม. |
| ค่าเงิน | THB=X | ดอลลาร์ | ใช้แปลง USD เป็นบาท |

- ดึงแบบ batch ผ่าน TTL cache ที่ใช้ร่วมกันทั้งแชทและ scheduler
- ไม่ poll ตลาดที่ปิด (แบบง่ายใน MVP, `exchange_calendars` ใน v2)
- ทุกข้อความบอกเวลาของราคาและความล่าช้า ถ้าแหล่งข้อมูลล่มให้บอกว่า "ข้อมูลล่าสุดเมื่อ ..."
- v2: ราคาทองบาทละ เริ่มจากค่าประมาณที่แปลงจาก GC=F และติดป้ายว่าประมาณการ

---

## 8. จุดออกแบบที่เล่าตอนสัมภาษณ์

| ประเด็น | ออกแบบยังไง | พิสูจน์ด้วย |
|---|---|---|
| ดึงข้อมูลครั้งเดียวต่อ symbol | รวม symbol จากทุก alert แล้วดึง batch เดียว, TTL cache + single-flight | เทสต์นับ call, ตัวเลข call ที่ประหยัดได้ |
| กันแจ้งเตือนซ้ำ | state (armed/disarmed) + hysteresis 0.5% + cooldown 30 นาที, alert แบบ % ยิงวันละครั้ง | backtest กับราคาที่แกว่งรอบเป้า |
| Job แบบ idempotent | AlertEvent (unique alert + dedupe key) ใน transaction เดียวกับ state (outbox), Postgres ใช้ `FOR UPDATE SKIP LOCKED` | เทสต์รันซ้ำ/รันซ้อนไม่ส่งซ้ำ |
| Rate limit ของ Telegram | คิวส่งแบบ token bucket, เคารพ `429 retry_after`, retry รอบหน้า | เทสต์จำลองตลาดดิ่งแล้ว alert ยิงพร้อมกัน |
| `callback_data` ≤ 64 bytes | รหัสสั้น `คำสั่ง:id`, ปุ่มกดซ้ำได้อย่างปลอดภัย | เทสต์ encode/decode, กดปุ่มของ alert ที่ลบแล้ว |
| Webhook | เช็ค secret token แบบ constant-time, กันซ้ำด้วย `update_id`, secret อยู่ใน env | เทสต์ secret ผิดได้ 401, update ซ้ำทำครั้งเดียว |
| เวลา | เก็บ UTC, แสดง Asia/Bangkok, รู้เวลาตลาดที่ขยับตาม DST | เทสต์ช่วงเปลี่ยน DST ของ US |
| แยก layer | `Messenger` และ `PriceProvider` เป็น interface, alert engine ไม่รู้จัก Telegram | v3: เพิ่ม LINE adapter โดยไม่แก้ engine |

ตัวเลขที่ควรเก็บไว้เล่า: ความหน่วงตั้งแต่ราคาข้ามเป้าจนถึงผู้ใช้ (p50/p95), สัดส่วน cache hit, จำนวน alert ที่ hysteresis กันได้

---

## 9. Roadmap

| เฟส | งาน | เสร็จเมื่อ |
|---|---|---|
| **MVP** | `/price` การ์ดราคา + รีเฟรช, watchlist, alert ราคาเป้าและ %, ตั้ง alert ด้วยปุ่ม + เลิกทำ, `/demo`, ช่วงห้ามรบกวน, yfinance + cache, ไม่ poll ตลาดปิด, เทสต์, deploy, README | คนแปลกหน้ากดลิงก์บอทแล้วเห็น alert เด้งด้วย `/demo` |
| **v2** | เวลาตลาด (`exchange_calendars`), alert 52 สัปดาห์ / SMA50/200 / RSI (คำนวณวันละครั้งหลังตลาดปิด), สรุปตลาดรายวัน, กราฟเป็นรูป, Finnhub WebSocket, ราคาทองบาทละ | วัดความหน่วงของ alert ได้และโชว์ตัวเลขใน README |
| **v3** (ถ้ามีแรง) | LINE adapter, Mini App, provider fallback, GitHub Actions CI, README + diagram ภาษาอังกฤษ | เพิ่ม LINE ได้โดยไม่แก้ alert engine |

ยังไม่ได้กำหนดวันที่ของแต่ละเฟส

### 9.1 แนวทางพัฒนา MVP

**เริ่มจากโครงที่รันได้ (walking skeleton) แล้วทำทีละ vertical slice** ไม่ทำแบบทีละชั้น (DB ทั้งหมด → service ทั้งหมด → handler ทั้งหมด) เพราะ:

1. แบบทีละชั้นต้องรอนานกว่าจะมีอะไรรันได้ ตรงกับความเสี่ยง "ขอบเขตบาน" ใน §10
2. schema ที่ออกแบบล่วงหน้ามักผิด เพราะยังไม่รู้ว่า handler จริงต้องใช้ข้อมูลอะไร
3. ความเสี่ยงใหญ่สุดอยู่ที่ infra (yfinance ถูกบล็อกจาก IP ของ cloud, host sleep) จึงต้อง deploy ให้เร็วเพื่อรู้ตั้งแต่ต้น

**โค้ดก่อนหรือ DB ก่อน:** ออกแบบ domain type ในโค้ดก่อน (`PriceSnapshot`, alert state ที่ใช้ `Decimal`) แล้วเพิ่มตารางเมื่อ slice ไหนต้องใช้ ใน slice เดียวกันเขียนจากในออกนอก: domain/rule → service → DB → handler

### 9.2 ขั้นตอน MVP

**ขั้น 0 — เตรียมโปรเจกต์** ✅ เสร็จ 25 พ.ย. 2026 (commit `671c558`)
- [x] สร้างบอทกับ BotFather (username ต้องลงท้ายด้วย `bot`) เก็บ token ใน `.env`
- [x] `git init` (branch `main`), `.gitignore`, `.env.example`
- [x] `pyproject.toml`, ruff, pytest, settings object ที่อ่าน env
- เสร็จเมื่อ: `ruff check` และ `pytest` ผ่าน
- สิ่งที่ตัดสินใจในขั้นนี้: ใช้ pydantic-settings, token เป็น `SecretStr` (ไม่หลุดเข้า log), `extra="forbid"` (พิมพ์ชื่อตัวแปรใน `.env` ผิดแล้ว error ทันที), ไม่สร้าง `Settings()` ตอน import (ให้ `main.py` สร้าง), เทสต์ใช้ `_env_file=None` เพื่อไม่พึ่ง `.env` จริง

**ขั้น 1 — Walking skeleton** ✅ เสร็จ 26 พ.ย. 2026 (branch `feat/walking-skeleton` ยังไม่ได้ merge เข้า `main`)
- [x] FastAPI + python-telegram-bot แบบ long polling
- [x] `/start` ตอบสองภาษาผ่าน messages module (เลือกจาก `language_code`)
- [x] ตั้งค่า logging
- เสร็จเมื่อ: กด `/start` ในเทเลแกรมแล้วได้คำตอบตามภาษาของเครื่อง
- สิ่งที่ตัดสินใจในขั้นนี้:
  - ภาษาเริ่มต้นเป็นไทย (ดู §1)
  - `messages.py` เก็บข้อความเป็น dict ที่ใช้ id เป็น key ก่อน แล้วค่อยแยก `th`/`en` ข้างใน, `t()` ที่เจอ id ที่ไม่มีจะ raise `KeyError` ทันที ดีกว่าส่งข้อความว่างไปให้ผู้ใช้แบบเงียบๆ
  - รันบอทใน lifespan ของ FastAPI ไม่ใช้ `run_polling()` เพราะ uvicorn คุม event loop อยู่แล้ว เปิดตามลำดับ `initialize` → `updater.start_polling` → `start` และปิดย้อนลำดับ เพื่อไม่ให้รับ update ใหม่หลังจาก handler หยุดแล้ว
  - uvicorn รันแบบ `--factory` ผ่าน `create_app()` ทำให้ `Settings()` ถูกสร้างตอนเปิดแอป ไม่ใช่ตอน import
  - logger ของ `httpx` ตั้งไว้ที่ WARNING เพราะที่ระดับ INFO มัน log URL ของทุก request และ URL ของ Telegram มี token อยู่
  - มี `/health` ไว้เช็คว่าแอปยังทำงานอยู่ (ใช้ต่อตอน deploy ในขั้น 3)

**ขั้น 2 — Slice `/price`**
- [ ] ตาราง alias ของ symbol (`PTT` → `PTT.BK`, `ทอง` → `GC=F`)
- [ ] interface `PriceProvider` + fake + yfinance, แปลงเป็น `Decimal` ที่ขอบ provider
- [ ] TTL cache + single-flight
- [ ] การ์ดราคาที่บอกเวลาและความล่าช้า + disclaimer
- [ ] โมดูล callback_data (encode/decode, assert ≤ 64 bytes) + ปุ่มรีเฟรช
- เสร็จเมื่อ: `/price NVDA`, `ราคา PTT`, `ทอง` ได้การ์ด และปุ่มรีเฟรชแก้ข้อความเดิม

**ขั้น 3 — Deploy เร็ว (เช็คความเสี่ยง)**
- [ ] Dockerfile, ขึ้น Fly.io หรือ Railway แบบ long polling
- เสร็จเมื่อ: `/price` ใช้ได้จาก host จริง (พิสูจน์ว่า yfinance ไม่ถูกบล็อกจาก IP ของ host)

**ขั้น 4 — Slice watchlist** (DB เริ่มตรงนี้: `users`, `watchlist_items`)
- [ ] SQLAlchemy 2 + migration, Postgres ใน docker-compose
- [ ] เปิด session ต่อ update, transaction อยู่ใน service layer
- [ ] `/watch`, `/portfolio`, ปุ่มเพิ่ม/เอาออกที่อ้างด้วย id
- [ ] ปุ่มเก่าของรายการที่ลบแล้วตอบ "รายการนี้ถูกลบไปแล้ว"
- เสร็จเมื่อ: เพิ่ม/ลบหุ้นในพอร์ตได้ และพอร์ตดึงราคาแบบ batch

**ขั้น 5 — แกน alert (pure, TDD)** (ทำต่อจากขั้น 2 ได้เลยถ้าอยากทำก่อน)
- [ ] rule ราคาเป้าและ %: armed/disarmed, hysteresis 0.5%, cooldown 30 นาที, alert แบบ % ยิงวันละครั้ง
- [ ] backtest กับราคาที่แกว่งรอบเป้า
- เสร็จเมื่อ: เทสต์ผ่านทั้งหมด โดยไม่แตะ Telegram หรือ DB

**ขั้น 6 — Slice alert ครบวง** (`alerts`, `alert_events`)
- [ ] `/alert NVDA < 120` แบบพิมพ์
- [ ] APScheduler ทุก 60 วิ (`max_instances=1`), ข้ามตลาดที่ปิดแบบง่าย
- [ ] engine: ดึงราคา batch → rule → อัปเดต state + insert `AlertEvent` ใน transaction เดียว (unique alert + dedupe key) → ส่งผ่าน `Messenger`
- เสร็จเมื่อ: ตั้ง alert แล้วเด้งจริง และเทสต์ว่ารัน cycle ซ้ำแล้วไม่ส่งซ้ำ

**ขั้น 7 — UX ปุ่ม + `/demo`**
- [ ] flow ตั้ง alert ด้วยปุ่ม: แก้ข้อความเดิม, ตัวเลือก %, `ForceReply` สำหรับราคาเอง, ปุ่มเลิกทำ
- [ ] `/alerts` พร้อมปุ่มหยุด/ลบ
- [ ] `/demo` เด้งภายใน 10 วินาที
- เสร็จเมื่อ: ตั้ง alert ได้ใน 1–3 ครั้งที่กด

**ขั้น 8 — Hardening** (`processed_updates`)
- [ ] send queue แบบ token bucket + รอตาม `429 retry_after`
- [ ] ช่วงห้ามรบกวน (`disable_notification`) + `/settings`
- [ ] เปลี่ยนเป็น webhook: เช็ค secret แบบ constant-time + กัน update ซ้ำด้วย `update_id`
- [ ] log วงจรชีวิต alert (fired, queued, sent, retried)
- เสร็จเมื่อ: มีเทสต์ครบทุกข้อใน §8

**ขั้น 9 — Ship MVP**
- [ ] deploy แบบ webhook
- [ ] README ภาษาอังกฤษ + diagram
- [ ] tag `mvp`
- เสร็จเมื่อ: คนแปลกหน้ากดลิงก์บอทแล้วเห็น alert เด้งจาก `/demo`

v2 และ v3 เริ่มหลัง tag `mvp` เท่านั้น

### 9.3 วิธีทำแต่ละ slice

1. แตก branch `feat/<ชื่อ>` จาก `main`
2. ออกแบบ interface และข้อความที่ผู้ใช้จะเห็นก่อน
3. เขียนเทสต์ของส่วน pure ก่อน (rule, alias, callback encode/decode)
4. Implement จากในออกนอก: domain → service → DB → handler
5. ลองในเทเลแกรมจริง
6. ส่งโค้ดให้ Claude รีวิว แล้วแก้ตามที่เจอ
7. Squash merge เข้า `main` (1 commit ต่อ 1 feature)

### 9.4 คำถามที่ต้องตอบก่อนถึงขั้นไหน

| คำถาม | ต้องตอบก่อน |
|---|---|
| host (Fly.io หรือ Railway) | ขั้น 3 |
| Postgres (Neon หรือ Supabase), ใช้ Alembic ไหม | ขั้น 4 |
| % ค่าเริ่มต้นต่อกลุ่มสินทรัพย์ | ขั้น 7 |
| เปิดให้คนทั่วไปใช้ หรือเฉพาะคนที่ได้ลิงก์ | ขั้น 9 |

---

## 10. ความเสี่ยง

| ความเสี่ยง | ผลกระทบ | ทางรับมือ |
|---|---|---|
| yfinance โดน 429/บล็อกจาก IP ของ cloud | ดึงราคาไม่ได้, alert เงียบ | cache + ไม่ poll ตลาดปิด, บอกเวลาข้อมูลล่าสุด, v2 มี Finnhub เป็น fallback |
| Host แบบ free tier sleep | scheduler หยุด, alert ไม่ยิง | ใช้ instance ที่เปิดตลอด |
| ขอบเขตบาน | ทำไม่เสร็จ ไม่มีอะไรให้โชว์ | deploy MVP ให้ได้ก่อนเริ่ม v2 |
| คำพูดที่ดูเหมือนแนะนำการลงทุน | เสียความน่าเชื่อถือ | ใช้คำที่เป็นข้อเท็จจริง และมี disclaimer "ไม่ใช่คำแนะนำการลงทุน" |

---

## 11. คำถามที่ยังเปิดอยู่

- [x] ชื่อโปรเจกต์: **PriceBell** (ตัดสินใจ 25 พ.ย. 2026)
- [ ] % ที่เสนอเป็นค่าเริ่มต้นต่อกลุ่มสินทรัพย์ (หุ้นไทย 3%, หุ้น US 5–10%?)
- [x] Telegram library: **python-telegram-bot** (ตัดสินใจ 25 พ.ย. 2026)
- [ ] เปิดให้คนทั่วไปใช้ได้ไหม หรือจำกัดเฉพาะคนที่ได้ลิงก์ (กระทบการจำกัด alert ต่อคนและการกันใช้งานผิดประเภท)
- [ ] ใช้ Alembic ทำ migration ไหม (แนะนำให้ใช้ตั้งแต่ตารางแรก เพราะตารางเพิ่มทีละ slice และ migration แต่ละไฟล์เป็นประวัติที่คนสัมภาษณ์อ่านได้)

---

## 12. ขั้นต่อไป

ขั้น 0 และขั้น 1 เสร็จแล้ว ให้ squash merge `feat/walking-skeleton` เข้า `main` ก่อน แล้วต่อด้วย **ขั้น 2 (Slice `/price`)** ใน §9.2 บน branch ใหม่ แล้วไล่ตามลำดับ คำถามที่ยังเปิดอยู่ให้ตอบก่อนถึงขั้นที่ระบุใน §9.4

---

## หมายเหตุ

- MVP เวอร์ชัน LINE ที่เคย scaffold ไว้ก่อนวางแผน ถูกย้ายไปถังขยะที่
  `~/.Trash/pricebell-mvp-20261125-101237` โค้ดส่วน provider, cache, alert rules (hysteresis/cooldown/outbox) และเทสต์ในนั้นยังใช้ต่อกับ Telegram ได้ ถ้าต้องการก็กู้คืนได้
