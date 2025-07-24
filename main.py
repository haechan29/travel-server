from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],  # React 앱 주소
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="images"), name="images")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
valid_access_code = os.getenv("VALID_ACCESS_CODE")

class CodeRequest(BaseModel):
  access_code: str

@app.post("/api/verify-code")
def verify_code(request: CodeRequest):
  if request.access_code == valid_access_code:
    return JSONResponse(content={"valid": True, "message": "유효한 코드입니다."})
  else:
    return JSONResponse(content={"valid": False, "message": "코드가 유효하지 않습니다."})

@app.get("/api/tours")
def get_tours(
  location: str = Query(None),
  access_code: str = Query(None)
):
  if access_code == valid_access_code:
    return get_tours_from_open_ai(location)
  else:
    return get_tours_hardcoding(location)

@app.get("/api/tours/continue")
def get_continued_tours(
  access_code: str = Query(None),
  previous_response_id: str = Query(None),
  condition: str = Query(None)
) -> JSONResponse:
  if access_code == valid_access_code:
    return get_continued_tours_from_open_ai(previous_response_id, condition)
  else:
    return get_continued_tours_hardcoding()
  
@app.get("/api/destinations")
def get_destinations():
  destinations = [
    {
        "name": "한라산",
        "code": "한라산",
        "image": "http://localhost:8000/images/hallasan.jpg",
        "description": "계절마다 다른 풍경을 보여주는 제주도의 상징, 한라산"
    },
    {
        "name": "우도",
        "code": "우도",
        "image": "http://localhost:8000/images/udo.jpg",
        "description": "제주 바다 너머 하얀 백사장과 검은 현무암이 어우러진 섬, 우도"
    },
    {
        "name": "협재 해변",
        "code": "협재 해변",
        "image": "http://localhost:8000/images/hyeopjae.jpg",
        "description": "맑고 에메랄드빛 바다, 조용하고 아름다운 제주 협재 해변"
    }
  ]
  return JSONResponse(content=destinations)

def get_tours_from_open_ai(location: str = None) -> JSONResponse:
  prompt = f"""
  마이리얼트립에서 제주도의 {location}을 포함하는 여행 상품을 최대 10개 추천해줘.
  
  아래 설명을 참고해서, 응답을 JSON 형식으로 생성해줘. 설명은 예시가 아니라 응답 필드의 명세야.
  구조에 맞는 실제 예시 데이터를 포함한 JSON을 생성해줘.
  응답은 반드시 ``` 코드 블록 없이 JSON만 순수하게 출력해줘.

  출력에는 구조에 맞는 실제 예시 데이터를 포함해줘.  
  filter.options[].value 값은 반드시 items[].attributes[key]의 값과 일치해야 해.
  attributes 에 포함되는 모든 value는 반드시 string 타입이어야 하며, 숫자/날짜/불리언 등의 값도 string으로 변환해서 제공해야 해.
  상품이 하나도 없다면 items와 filter이 빈 배열인 응답을 내려줘.

  [응답 구조 설명]
  - 실제 response의 id
  - items: 여행 상품 배열
    - item: 여행 정보를 담는 객체
      - title: 여행 상품의 제목
      - link: 상품 링크
      - course: 여행 코스 설명
      - price: 여행 상품 가격 (숫자)
      - region: 여행 상품의 지역 (지번 기준, 읍/면/리까지만)
      - attributes: 세부 정보 객체
        - location: 실제 장소 (게시글에 적힌 정확한 위치)
        - operating_hour: 운영 시간
        - 기타 필요한 세부 정보도 포함 가능

  - filters: 필터 항목 배열
    - filter: 공통 속성 기반 필터 항목
      - key: attributes 내 필드 이름
      - label: 사용자에게 보여줄 필터 이름
      - type: single_select 또는 multi_select
      - options: 선택 가능한 옵션들
        - option:
          - label: 사용자에게 보여줄 옵션 이름
          - value: 실제 attributes의 값과 일치하는 값

  [응답 예시]
  {{
    "filters": [
      {{
        "key": "duration",
        "label": "소요 시간",
        "type": "single_select",
        "options": [
          {{
            "label": "1시간",
            "value": "1시간"
          }},
          {{
            "label": "2시간",
            "value": "2시간"
          }}
        ]
      }}
    ],
    "items": [
      {{
        "title": "[협재] 스튜디오/단체 - 사진작가와 함께하는 협재해변 산책(프라이빗 스냅)",
        "link": "https://www.myrealtrip.com/offers/72765",
        "course": "야자수 길 → 협재 에메랄드빛 해변 스냅 트래킹",
        "price": 150000,
        "region": "제주시 한림읍",
        "attributes": {{
          "location": "제주시 한림읍 협재리 해변 산책로",
          "operating_hour": "시간 협의",
          "duration": "1시간",
          "group_type": "프라이빗 또는 소규모 그룹",
          "photographer": "스튜디오 사진작가 포함"
        }}
      }},
      {{
        "title": "[협재] 라탄 공예 제주하면 떠오르는 한라봉 무드등 만들기 원데이 클래스",
        "link": "https://www.myrealtrip.com/guides/18585",
        "course": "협재 인근 라탄공방에서 무드등 제작 + 소품샵 관람",
        "price": 70000,
        "region": "제주시 한림읍",
        "attributes": {{
          "location": "제주시 한림읍 옹포리 협재 해수욕장 근처 라탄공방",
          "operating_hour": "10:30 - 20:00",
          "duration": "2시간",
          "closed_days": "매주 화요일 휴무",
          "class_type": "원데이 클래스",
          "includes": "재료, 포토존, 보조 도구 제공"
        }}
      }}
    ]
  }}
  """

  openai_response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search_preview"}],
    input=prompt
  )

  try:
    return JSONResponse(content={
      "id": openai_response.id,
      "output": openai_response.output_text
    })
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={
          "error": "AI 응답 파싱 실패",
          "raw_output": openai_response.output_text
      }
    )

def get_tours_hardcoding(location: str = None) -> JSONResponse:
  if location == "협재 해변":
    response = {
      "filters": [
        {
          "key": "duration",
          "label": "소요 시간",
          "type": "single_select",
          "options": [
            {
              "label": "1시간",
              "value": "1시간"
            },
            {
              "label": "2시간",
              "value": "2시간"
            }
          ]
        },
        {
          "key": "class_type",
          "label": "클래스 유형",
          "type": "single_select",
          "options": [
            {
              "label": "원데이 클래스",
              "value": "원데이 클래스"
            }
          ]
        },
        {
          "key": "group_type",
          "label": "그룹 구성",
          "type": "single_select",
          "options": [
            {
              "label": "프라이빗 또는 소규모 그룹",
              "value": "프라이빗 또는 소규모 그룹"
            }
          ]
        },
        {
          "key": "closed_days",
          "label": "휴무일",
          "type": "single_select",
          "options": [
            {
              "label": "매주 화요일 휴무",
              "value": "매주 화요일 휴무"
            }
          ]
        }
      ],
      "items": [
        {
          "title": "[협재] 스튜디오/단체 - 사진작가와 함께하는 협재해변 산책(프라이빗 스냅)",
          "link": "https://www.myrealtrip.com/offers/72765",
          "course": "야자수 길 → 협재 에메랄드빛 해변 스냅 트래킹",
          "price": 150000,
          "region": "제주시 한림읍",
          "attributes": {
            "location": "제주시 한림읍 협재리 해변 산책로",
            "operating_hour": "시간 협의",
            "duration": "1시간",
            "group_type": "프라이빗 또는 소규모 그룹",
            "photographer": "스튜디오 사진작가 포함"
          }
        },
        {
          "title": "[협재] 라탄 공예 제주하면 떠오르는 한라봉 무드등 만들기 원데이 클래스",
          "link": "https://www.myrealtrip.com/guides/18585",
          "course": "협재 인근 라탄공방에서 무드등 제작 + 소품샵 관람",
          "price": 70000,
          "region": "제주시 한림읍",
          "attributes": {
            "location": "제주시 한림읍 옹포리 협재 해수욕장 근처 라탄공방",
            "operating_hour": "10:30 - 20:00",
            "duration": "2시간",
            "closed_days": "매주 화요일 휴무",
            "class_type": "원데이 클래스",
            "includes": "재료, 포토존, 보조 도구 제공"
          }
        }
      ]
    }
  elif location == "우도":
    response = {
      "filters": [
        {
          "key": "type",
          "label": "상품 유형",
          "type": "single_select",
          "options": [
            { "label": "패키지 투어", "value": "패키지 투어" },
            { "label": "버스/티켓", "value": "버스/티켓" },
            { "label": "프라이빗 차량 투어", "value": "프라이빗 차량 투어" }
          ]
        },
        {
          "key": "duration",
          "label": "소요 시간",
          "type": "single_select",
          "options": [
            { "label": "5시간", "value": "5시간" },
            { "label": "시간 제한 없음", "value": "시간 제한 없음" }
          ]
        },
        {
          "key": "includes",
          "label": "포함 사항",
          "type": "multi_select",
          "options": [
            { "label": "왕복 승선료 포함", "value": "왕복 승선료 포함" },
            { "label": "순환버스 티켓", "value": "순환버스 티켓" },
            { "label": "가이드 포함", "value": "가이드 포함" }
          ]
        }
      ],
      "items": [
        {
          "title": "[우도] 제주도 우도 1일 버스여행 원데이 패키지",
          "link": "https://experiences.myrealtrip.com/products/3881278",
          "course": "우도 8경 탐방 → 녹차족욕",
          "price": 33800,
          "region": "제주시",
          "attributes": {
            "type": "패키지 투어",
            "duration": "5시간",
            "includes": "왕복 승선료 포함",
            "meeting_point": "제주공항, 탑동 등 픽업",
            "operating_hour": "10:30~15:30",
            "group_size": "단체"
          }
        },
        {
          "title": "[우도] 자유롭게 내리고 타는 우도 해안도로 순환버스 티켓",
          "link": "https://experiences.myrealtrip.com/products/3827776",
          "course": "우도 해안도로 전 구간 자유탐방",
          "price": 5000,
          "region": "제주시 우도면",
          "attributes": {
            "type": "버스/티켓",
            "duration": "시간 제한 없음",
            "includes": "순환버스 티켓",
            "operating_hour": "도항선 첫배~막배",
            "notes": "홀수일/짝수일 방향 다름"
          }
        },
        {
          "title": "[제주우도] 제주1번가 우도 자유 투어 (킴스제주 프라이빗)",
          "link": "https://experiences.myrealtrip.com/products/3739001",
          "course": "우도 + 동쪽 시즌별 명소 드라이빙",
          "price": 40000,
          "region": "제주시",
          "attributes": {
            "type": "프라이빗 차량 투어",
            "duration": "시간 제한 없음",
            "includes": "가이드 포함",
            "vehicle": "카니발 5인승",
            "meeting_point": "제주공항 또는 탑동 숙소",
            "group_size": "최대 5명",
            "cancel_policy": "7일 전 전액환불"
          }
        }
      ]
    }
  elif location == "한라산":
    response = {
      "filters": [
        {
          "key": "course_type",
          "label": "코스 유형",
          "type": "single_select",
          "options": [
            {
              "label": "영실 코스",
              "value": "영실 코스"
            },
            {
              "label": "성판악 코스",
              "value": "성판악 코스"
            },
            {
              "label": "백록담 눈꽃 트레킹",
              "value": "백록담 눈꽃 트레킹"
            }
          ]
        },
        {
          "key": "difficulty",
          "label": "난이도",
          "type": "single_select",
          "options": [
            {
              "label": "초보자용",
              "value": "초보자용"
            },
            {
              "label": "중난이도",
              "value": "중난이도"
            },
            {
              "label": "겨울 눈꽃 트레킹",
              "value": "겨울 눈꽃 트레킹"
            }
          ]
        },
        {
          "key": "duration",
          "label": "소요 시간",
          "type": "single_select",
          "options": [
            {
              "label": "4시간",
              "value": "4시간"
            },
            {
              "label": "4.5시간",
              "value": "4.5시간"
            },
            {
              "label": "12시간",
              "value": "12시간"
            }
          ]
        }
      ],
      "items": [
        {
          "title": "[한라산] 등산 비기너를 위한 한라산 투어 (영실 코스)",
          "link": "https://experiences.myrealtrip.com/products/3529682",
          "course": "영실 탐방로 입구 → 윗세오름 대피소 왕복",
          "price": 30000,
          "region": "제주시",
          "attributes": {
            "location": "영실 탐방로 입구 ~ 윗세오름 대피소",
            "operating_hour": "08:00~12:00",
            "course_type": "영실 코스",
            "difficulty": "초보자용",
            "duration": "4시간",
            "group_type": "가이드 포함",
            "frequency": "매일 진행"
          }
        },
        {
          "title": "[한라산] 하이킹/기부 하이킹 (성판악 코스)",
          "link": "https://experiences.myrealtrip.com/products/3529692",
          "course": "성판악 입구 → 백록담 정상 왕복",
          "price": 30000,
          "region": "제주시",
          "attributes": {
            "location": "한라산 국립공원 성판악 탐방안내소",
            "operating_hour": "06:00~16:30",
            "course_type": "성판악 코스",
            "difficulty": "중난이도",
            "duration": "4.5시간",
            "includes": "가이드, 도시락, 입장료",
            "cancel_policy": "3일 전 전액환불"
          }
        },
        {
          "title": "[한라산 백록담 눈꽃 트레킹]",
          "link": "https://experiences.myrealtrip.com/products/3827743",
          "course": "성판악 → 백록담 → 관음사 하산",
          "price": 120000,
          "region": "제주시",
          "attributes": {
            "location": "성판악 주차장 입구 ~ 백록담 정상",
            "operating_hour": "00:00~18:00",
            "course_type": "백록담 눈꽃 트레킹",
            "difficulty": "겨울 눈꽃 트레킹",
            "duration": "12시간",
            "equipment_included": "아이젠, 스패츠, 핫팩 등",
            "ot": "사전 OT zoom 포함"
          }
        }
      ]
    }
  else:
    response = {
      "filters": [],
      "items": [],
    }

  common_filters = [
    {
      "key": "price",
      "label": "가격",
      "type": "price",
    },
    {
      "key": "region",
      "label": "위치",
      "type": "region",
      "options": [
        { "label": "제주시 서귀포시 성산읍", "value": "제주시 서귀포시 성산읍" }
      ]
    }
  ]
  response["filters"] = common_filters + response["filters"]
  return JSONResponse(content={
    "id": 0,
    "output": response
  })

def get_continued_tours_from_open_ai(
  previous_response_id: str,
  condition: str
) -> JSONResponse:
  prompt = f"""
  아까의 적용 조건에 다음 조건을 추가해서 다시 최대 10개의 여행상품을 추천해줘.
  {condition}
  """

  openai_response = client.responses.create(
    model="gpt-4o",
    previous_response_id=previous_response_id,
    tools=[{"type": "web_search_preview"}],
    input=prompt
  )

  try:
    return JSONResponse(content={
      "id": openai_response.id,
      "output": openai_response.output_text
    })
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={
          "error": "AI 응답 파싱 실패",
          "raw_output": openai_response.output_text
      }
    )

def get_continued_tours_hardcoding() -> JSONResponse:
  if location == "협재 해변":
    response = {
      "filters": [
        {
          "key": "duration",
          "label": "소요 시간",
          "type": "single_select",
          "options": [
            { "label": "60분", "value": "60분" },
          ]
        },
        {
          "key": "operating_hour",
          "label": "운영 시간/만나는 시간",
          "type": "single_select",
          "options": [
            { "label": "오후 5시", "value": "오후 5시" },
          ]
        }
      ],
      "items": [
        {
          "title": "[협재] 제주의 일몰과 불멍의 매력 속으로!",
          "link": "https://www.myrealtrip.com/offers/100305",
          "course": "협재해수욕장 주차장 → 일몰 감상 후 불멍",
          "price": 90000,
          "region": "제주시 한림읍",
          "attributes": {
            "location": "협재해수욕장 주차장",
            "operating_hour": "오후 5시",
            "duration": "60분",
            "group_type": "프라이빗",
            "equipment": "담요, 모닥불 세트 제공"
          }
        }
      ]
    }
  elif location == "우도":
    response = {
      "filters": [
        {
          "key": "type",
          "label": "상품 유형",
          "type": "single_select",
          "options": [
            { "label": "패키지 투어", "value": "패키지 투어" },
            { "label": "버스/티켓", "value": "버스/티켓" }
          ]
        },
        {
          "key": "duration",
          "label": "소요 시간",
          "type": "single_select",
          "options": [
            { "label": "5시간", "value": "5시간" },
            { "label": "시간 제한 없음", "value": "시간 제한 없음" }
          ]
        },
        {
          "key": "includes",
          "label": "포함 사항",
          "type": "multi_select",
          "options": [
            { "label": "왕복 승선료 포함", "value": "왕복 승선료 포함" },
            { "label": "순환버스 티켓", "value": "순환버스 티켓" },
          ]
        }
      ],
      "items": [
        {
          "title": "[우도] 제주도 우도 1일 버스여행 원데이 패키지",
          "link": "https://experiences.myrealtrip.com/products/3881278",
          "course": "우도 8경 탐방 → 녹차족욕",
          "price": 33800,
          "region": "제주시",
          "attributes": {
            "type": "패키지 투어",
            "duration": "5시간",
            "includes": "왕복 승선료 포함",
            "meeting_point": "제주공항, 탑동 등 픽업",
            "operating_hour": "10:30~15:30",
            "group_size": "단체"
          }
        },
        {
          "title": "[우도] 자유롭게 내리고 타는 우도 해안도로 순환버스 티켓",
          "link": "https://experiences.myrealtrip.com/products/3827776",
          "course": "우도 해안도로 전 구간 자유탐방",
          "price": 5000,
          "region": "제주시 우도면",
          "attributes": {
            "type": "버스/티켓",
            "duration": "시간 제한 없음",
            "includes": "순환버스 티켓",
            "operating_hour": "도항선 첫배~막배",
            "notes": "홀수일/짝수일 방향 다름"
          }
        }
      ]
    }
  elif location == "한라산":
    response = {
      "filters": [
        {
          "key": "course_type",
          "label": "코스 유형",
          "type": "single_select",
          "options": [
            {"label": "영실 코스", "value": "영실 코스"}
          ]
        },
        {
          "key": "difficulty",
          "label": "난이도",
          "type": "single_select",
          "options": [
            {"label": "초보자용", "value": "초보자용"}
          ]
        },
        {
          "key": "duration",
          "label": "소요 시간",
          "type": "single_select",
          "options": [
            {"label": "4시간", "value": "4시간"},
          ]
        }
      ],
      "items": [
        {
          "title": "[한라산] 등산 비기너를 위한 한라산 투어 (영실 코스)",
          "link": "https://experiences.myrealtrip.com/products/3529682",
          "course": "영실 탐방로 입구 → 윗세오름 대피소 왕복",
          "price": 30000,
          "region": "제주시",
          "attributes": {
            "location": "영실 탐방로 입구 ~ 윗세오름 대피소",
            "operating_hour": "08:00~12:00",
            "course_type": "영실 코스",
            "difficulty": "초보자용",
            "duration": "4시간",
            "group_type": "가이드 포함",
            "frequency": "매일 진행"
          }
        }
      ]
    }
  else:
    response = {
      "filters": [],
      "items": [],
    }

  common_filters = [
    {
      "key": "price",
      "label": "가격",
      "type": "price",
    },
    {
      "key": "region",
      "label": "위치",
      "type": "region",
      "options": [
        { "label": "제주시 서귀포시 성산읍", "value": "제주시 서귀포시 성산읍" }
      ]
    }
  ]
  response["filters"] = common_filters + response["filters"]
  return JSONResponse(content={
    "id": 0,
    "output": response
  })