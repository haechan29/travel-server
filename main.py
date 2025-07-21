from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/tours")
def get_tours():
    response = {
  "filters": [
    {
      "key": "duration",
      "label": "소요 시간",
      "type": "single_select",
      "options": [
        { "label": "10시간", "value": "10시간" },
        { "label": "11시간", "value": "11시간" },
        { "label": "12시간", "value": "12시간" }
      ]
    },
    {
      "key": "transport",
      "label": "이동 수단",
      "type": "single_select",
      "options": [
        { "label": "버스 포함", "value": "버스 포함" },
        { "label": "셔틀버스", "value": "셔틀버스" }
      ]
    },
    {
      "key": "extras",
      "label": "추가 요소",
      "type": "multi_select",
      "options": [
        { "label": "만좌모, 코우리섬 포함", "value": "만좌모, 코우리섬 포함" },
        { "label": "수중 잠수함 포함", "value": "수중 잠수함 포함" }
      ]
    }
  ],
  "items": [
    {
      "title": "오키나와 버스투어 북부 1일 – 츄라우미 수족관 포함",
      "link": "https://experiences.myrealtrip.com/products/3154181",
      "course": "만좌모 → 코우리대교 → 츄라우미 수족관 (3시간) → 아메리칸 빌리지",
      "price": 48000,
      "region": "일본 오키나와 북부",
      "attributes": {
        "location": "만좌모, 코우리대교, 츄라우미 수족관, 아메리칸 빌리지",
        "duration": "10시간",
        "transport": "셔틀버스",
        "extras": "만좌모, 코우리섬 포함",
        "guide_language": "한국어",
        "ticket_included": "츄라우미 수족관 포함"
      }
    },
    {
      "title": "(나하/차탄 출발) 츄라시마 종일 관광버스 C코스",
      "link": "https://experiences.myrealtrip.com/products/3511485",
      "course": "츄라우미 수족관 → 코우리대교 → 만좌모 등 포함",
      "price": 54201,
      "region": "일본 오키나와 북부",
      "attributes": {
        "location": "츄라우미 수족관, 코우리섬, 만좌모",
        "duration": "11시간",
        "transport": "버스 포함",
        "extras": "만좌모, 코우리섬 포함",
        "ticket_included": "츄라우미 수족관 포함",
        "guide_language": "한국어 음성 가이드"
      }
    },
    {
      "title": "츄라우미 수족관 & 아메리칸 빌리지 & 수중 잠수함 투어",
      "link": "https://experiences.myrealtrip.com/products/3885703",
      "course": "수중 잠수함 → 츄라우미 수족관 2시간 → 아메리칸 빌리지",
      "price": 65900,
      "region": "일본 오키나와 북부",
      "attributes": {
        "location": "츄라우미 수족관, 아메리칸 빌리지, 수중 잠수함",
        "duration": "12시간",
        "transport": "버스 포함",
        "extras": "수중 잠수함 포함",
        "ticket_included": "츄라우미 수족관 포함",
        "guide_language": "다국어 (한/일/영)"
      }
    }
  ]
}
    return JSONResponse(content=response)