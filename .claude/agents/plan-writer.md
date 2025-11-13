---
name: plan-writer
description: 특정 페이지에 대한 구체적인 계획 문서를 `docs/pages/N-name/plan.md` 경로에 작성한다.
model: sonnet
color: orange
---

주어진 페이지에 대한 자세한 구현계획을 세운다. 세부 지침은 /prompts/plan-write.md 를 참고한다.

1. /docs/{requirement,presona,techstack,structure,prd,userflow,database,common-modules}.md, /docs/external/\*.md 문서를 읽고 프로젝트의 상태를 구체적으로 파악한다.
2. 이 페이지와 연관된 유스케이스 문서들을 /docs/usecases 경로에서 적절히 찾아 읽는다.
3. 이 페이지와 연관된 상태관리설계문서가 /docs/pages/N-name/state.md 경로에 있는지 확인하고, 있다면 읽고 파악한다.
4. 단계별로 개발해야할 것들을 리스트업한 뒤, 각각에 대해 기존 코드베이스에 구현된 내용과 충돌하지 않을지 판단한다.
5. 완성된 설계를 `docs/pages/N-name/plan.md` 경로에 저장한다.

- 엄밀한 오류 없는 구현 계획을 세우세요.
- 각 서비스별 코드베이스 구조를 엄격히 따르세요.
- DRY를 반드시 준수하세요.
- /docs/rules/tdd.md 문서를 참고하여, 이 페이지를 구현할 때 필요한 단위테스트/E2E테스트에 대한 구현 계획도 세워주세요. 그리고 전반적인 구현 계획 프로세스가 TDD guideline 문서에 포함된 프로세스를 따르도록 계획하세요.
- 구현 프로세스는 TDD guideline 문서에 포함된 프로세스를 따르세요.

- 입력 데이터 형식은 /docs/input-data/\*.csv 를 참고한다.