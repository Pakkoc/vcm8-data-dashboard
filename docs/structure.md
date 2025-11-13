알겠습니다. YC 배치 스타트업 CTO로서, MVP의 빠른 반복(iteration)과 장기적인 코드 품질을 모두 만족시키는 최종 아키텍처 제안서를 작성했습니다.

이 문서는 그대로 복사하여 팀 내부 개발 가이드 또는 프로젝트 설계 문서로 즉시 활용할 수 있도록 구성되었습니다.

---

### **[Final] 대학교 데이터 시각화 대시보드 Codebase Architecture 제안**

**핵심 철학: 변경에 유연하고, 테스트가 용이하며, 확장에 용이한 구조**

우리의 목표는 단순히 MVP를 빠르게 만드는 것을 넘어, 첫 베타테스트 이후 쏟아질 피드백을 즉시 반영하여 제품을 빠르게 개선해나가는 것입니다. 이를 위해 모든 코드는 **'자신의 역할에만 충실하고, 주변에 미치는 영향을 최소화'**하도록 설계합니다.

`Layered Architecture`를 기반으로 **저장소 패턴(Repository Pattern)**을 도입하여 각 계층의 책임을 명확히 분리합니다. 이는 SOLID 원칙, 특히 **단일 책임 원칙(SRP)**과 **의존성 역전 원칙(DIP)**을 자연스럽게 준수하도록 합니다.

**데이터 흐름: `View` → `Service` → `Repository` → `Model(ORM)`**
이 명확한 단방향 의존성 흐름은 코드의 예측 가능성을 높이고, 각 파트가 독립적으로 테스트될 수 있는 강력한 기반이 됩니다.

---

### 1. 백엔드 (Django + DRF) 아키텍처

#### **Directory Structure**

```
/backend
├── dashboard_project/         # Django 프로젝트 설정 폴더
├── apps/                      # 모든 Django 앱들을 관리하는 폴더
│   ├── core/                  # 공통 모듈 (e.g., Base Models, Mixins)
│   ├── users/                 # 사용자 인증/인가 앱
│   └── dashboard/             # 핵심 기능 앱 (데이터 Import 및 시각화 API)
│       ├── __init__.py
│       ├── models.py          # <<-- Data Structure Layer (ORM 모델)
│       ├── repositories.py    # <<-- Data Access Layer (DB 소통 구현체)
│       ├── services/          # <<-- Business Logic Layer (순수 로직)
│       │   ├── __init__.py
│       │   ├── excel_importer.py  # 엑셀 파싱 및 데이터 가공 서비스
│       │   └── summary_generator.py # 대시보드 데이터 집계/요약 서비스
│       ├── serializers.py     # 데이터 직렬화 (API 입/출력 형식 정의)
│       ├── views.py           # <<-- Presentation Layer (API Endpoints)
│       ├── urls.py
│       └── tests/             # 단위/통합 테스트 코드
│           ├── test_services.py
│           └── test_repositories.py
└── manage.py
```

#### **Top Level Building Blocks & Responsibilities**

1.  **`views.py` (Presentation Layer)**
    *   **책임:** 오직 HTTP 요청(Request)을 받고 HTTP 응답(Response)을 보내는 역할만 합니다.
    *   **구현:** 클라이언트로부터 받은 데이터를 `Serializer`로 유효성 검증 후, 관련 `Service`에 전달합니다. Service의 실행 결과를 다시 `Serializer`를 통해 JSON으로 변환하여 반환합니다.
    *   **의존성:** 오직 `Service`와 `Serializer`에만 의존합니다. `Repository`나 ORM(`models.py`)의 존재를 알지 못합니다.

2.  **`services/` (Business Logic Layer)**
    *   **책임:** **애플리케이션의 핵심 두뇌입니다.** "엑셀 파일을 어떻게 파싱하는가?", "성과 지표를 어떤 기준으로 집계하는가?"와 같은 순수한 비즈니스 규칙을 구현합니다.
    *   **구현:** 프레임워크와 데이터베이스에 대한 의존성이 전혀 없는 **순수 Python 객체**로 작성합니다. `Repository`를 생성자나 메소드를 통해 **주입(Dependency Injection)**받아 사용합니다.
    *   **의존성:** `Repository`의 '추상적인 약속(인터페이스)'에만 의존합니다. Django ORM을 직접 임포트하지 않습니다.

3.  **`repositories.py` (Data Access Layer)**
    *   **책임:** **데이터베이스와의 모든 소통을 담당하는 유일한 창구입니다.** 비즈니스 로직(Service)과 데이터 영속성(ORM)을 분리하는 '방화벽' 역할을 합니다.
    *   **구현:** `Service`가 요청한 데이터를 저장(`save`), 조회(`find_by_id`), 수정(`update`)하는 구체적인 방법을 Django ORM을 사용하여 구현합니다.
    *   **의존성:** Django ORM(`models.py`)에 직접 의존합니다.

4.  **`models.py` (Data Structure Layer)**
    *   **책임:** 데이터베이스 테이블의 스키마를 정의합니다.

#### **데이터 흐름 예시: 엑셀 파일 업로드**

1.  **[View]** `FileUploadView`가 API 요청을 받습니다.
2.  **[View]** `Serializer`를 통해 파일이 유효한지 검증합니다.
3.  **[View]** `ExcelImportService` 인스턴스를 생성하고, `Repository` 구현체(`PerformanceDataRepository`)를 주입합니다.
4.  **[View]** `service.import_from_excel(file)` 메소드를 호출합니다.
5.  **[Service]** `ExcelImportService`는 `pandas`로 엑셀 파일을 읽고, 데이터를 정제하여 `PerformanceData` 객체 리스트를 만듭니다. (이 과정은 DB와 무관합니다)
6.  **[Service]** 주입받은 `repository.save_all(performance_data_list)`를 호출하여 "저장해줘"라고 명령합니다.
7.  **[Repository]** `PerformanceDataRepository`는 `PerformanceData.objects.bulk_create()`와 같은 Django ORM 메소드를 사용하여 실제 DB에 데이터를 저장합니다.
8.  **[View]** 성공 결과를 받아 클라이언트에게 `201 Created` 응답을 반환합니다.

---

### 2. 프론트엔드 (React + Vite) 아키텍처

#### **Directory Structure**

```
/frontend
├── public/
├── src/
│   ├── api/                   # <<-- External Communication Layer
│   │   ├── index.js           # Axios 인스턴스 설정 (baseURL, interceptors)
│   │   └── dashboardAPI.js    # 대시보드 관련 모든 API 호출 함수
│   ├── components/            # 재사용 가능한 순수 UI 컴포넌트 (Dumb Components)
│   │   ├── charts/
│   │   ├── common/
│   │   └── layout/
│   ├── hooks/                 # 커스텀 훅 (e.g., useApi, useAuth)
│   ├── pages/                 # 라우팅 단위 페이지 (Smart Components)
│   │   ├── DashboardPage.jsx
│   │   └── UploadPage.jsx
│   ├── store/                 # 전역 상태 관리 (Zustand or Jotai 추천)
│   │   └── userStore.js
│   ├── utils/                 # 순수 헬퍼 함수 (e.g., date formatting)
│   ├── App.jsx                # 라우팅 정의
│   └── main.jsx
└── package.json
```

#### **Top Level Building Blocks & Responsibilities**

1.  **`pages/` (Smart Components)**
    *   **책임:** 애플리케이션의 '상태'를 소유하고 비즈니스 로직을 처리합니다. `api`를 호출하여 데이터를 가져오고, `store`의 상태를 업데이트하며, `components`에 데이터를 `props`로 전달합니다.

2.  **`components/` (Dumb Components)**
    *   **책임:** 오직 `props`를 받아 화면을 그리는 역할만 합니다. 자체적으로 상태를 가지거나 API를 호출하지 않습니다. 재사용성과 예측 가능성을 극대화합니다.

3.  **`api/` (External Communication Layer)**
    *   **책임:** **백엔드와의 모든 통신을 중앙에서 관리하는 방화벽입니다.** `axios`나 `fetch`를 사용하여 HTTP 요청을 보내는 로직을 모두 이곳에 캡슐화합니다.
    *   **구현:** 컴포넌트는 `dashboardAPI.getSummary()`와 같은 함수를 호출하기만 하면 됩니다. 실제 endpoint URL, HTTP 메소드, 에러 핸들링 등은 이 레이어에서 처리합니다.

---

### **결론: 이 구조가 최적인 이유**

1.  **최고 수준의 테스트 용이성:** `Service Layer`는 DB 연결 없이 가짜 `Repository(Mock Repository)`를 주입하여 순수 로직을 수 밀리초(ms) 단위로 빠르게 테스트할 수 있습니다. 이는 안정적인 코드 품질을 보장하는 핵심입니다.
2.  **명확한 단일 책임:** "엑셀 파싱 규칙 변경"은 `services/`만, "DB 쿼리 성능 개선"은 `repositories.py`만, "API 응답 형식 변경"은 `serializers.py`만 수정하면 됩니다. 각자의 책임이 명확하여 유지보수가 극도로 쉬워집니다.
3.  **유연한 확장성:** 미래에 Supabase가 아닌 다른 DB를 사용하거나, 특정 데이터를 파일로 저장해야 할 때도 비즈니스 로직인 `Service`는 단 한 줄도 건드리지 않고 `Repository`의 구현만 교체하면 됩니다.
4.  **속도와 안정성의 균형:** 이 구조는 MVP 단계에서 오버엔지니어링이 아닙니다. 오히려 **가장 복잡하고 중요한 비즈니스 로직을 처음부터 안정적으로 분리**하여, 이후의 잦은 변경 요청에 훨씬 더 빠르고 자신감 있게 대응할 수 있도록 만드는 **지속 가능한 속도를 위한 최적의 투자**입니다.

이 아키텍처를 기반으로 즉시 개발에 착수하여, 시장의 가설을 가장 빠르고 안정적으로 검증해 나가겠습니다.