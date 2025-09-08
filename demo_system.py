#!/usr/bin/env python3
"""
멀티에이전트 시스템 실시간 데모 스크립트
"""

import asyncio
import time
from src.core.langgraph_pipeline import run_agent_pipeline
from src.config import GOOGLE_DRIVE_FOLDER_ID

def show_system_flow():
    """시스템 흐름을 시각적으로 표시"""
    print("[TARGET] 학생회 규정 관리 멀티에이전트 시스템")
    print("=" * 60)
    print()
    print("[CHART] 시스템 구조:")
    print()
    print("    [사용자 질문]")
    print("         ↓")
    print("    [질문 라우팅] ← 학생회 업무 관련성 판단")
    print("         ↓")
    print("    [병렬 에이전트 실행]")
    print("         ├── [DOC] 규정 검토 에이전트")
    print("         └── [SEARCH] 감사 에이전트")
    print("         ↓")
    print("    [BALANCE] 조정 에이전트 ← 결과 종합 및 최종 권고")
    print("         ↓")
    print("    [FILE] 최종 분석 결과")
    print()
    print("=" * 60)

async def demo_workflow():
    """실제 워크플로우 실행 데모"""
    test_query = "학생회비로 회식비 사용이 가능한가요?"
    folder_id = GOOGLE_DRIVE_FOLDER_ID
    
    if not folder_id:
        print("[ERROR] Google Drive 폴더 ID가 설정되지 않았습니다.")
        return
    
    print(f"[FIRE] 실시간 처리 시작!")
    print(f"[CHAT] 질문: '{test_query}'")
    print()
    
    # 단계별 진행 표시
    steps = [
        "[ROCKET] 시스템 초기화...",
        "[SEARCH] 질문 라우팅 중...",
        "[DOC] 규정 검토 에이전트 실행 중...",
        "[SEARCH] 감사 에이전트 실행 중...", 
        "[BALANCE] 조정 에이전트가 결과 종합 중...",
        "[WRITE] Notion에 결과 기록 중...",
        "[CHECK] 처리 완료!"
    ]
    
    for i, step in enumerate(steps):
        print(f"[{i+1}/7] {step}")
        time.sleep(0.5)  # 시각적 효과
        
        if i == 6:  # 마지막 단계에서 실제 실행
            print("\n" + "="*60)
            print("[TARGET] 실제 에이전트 파이프라인 실행:")
            print("="*60)
            
            start_time = time.time()
            final_state = await run_agent_pipeline(test_query, folder_id)
            end_time = time.time()
            
            print(f"\n[TIMER] 총 처리 시간: {end_time - start_time:.2f}초")
            print("\n" + "="*60)
            print("[CHART] 최종 결과:")
            print("="*60)
            
            # 결과 출력
            sections = [
                ("[DOC] 규정 검토 에이전트 분석", final_state.get("reviewer_analysis", "분석 실패")),
                ("[SEARCH] 감사 에이전트 분석", final_state.get("auditor_analysis", "분석 실패")),
                ("[BALANCE] 최종 종합 분석 및 권고안", final_state.get("final_recommendation", "권고안 도출 실패"))
            ]
            
            for title, content in sections:
                print(f"\n{title}:")
                print("-" * 50)
                if len(content) > 200:
                    print(f"{content[:200]}...")
                    print(f"[전체 길이: {len(content)}자]")
                else:
                    print(content)
                print()

async def main():
    """메인 데모 함수"""
    show_system_flow()
    
    try:
        print("[GAME] 실시간 데모를 시작하시겠습니까? (y/n): ", end="")
        user_input = input()
        
        if user_input.lower() == 'y':
            await demo_workflow()
            print("\n[PARTY] 데모 완료! 멀티에이전트 시스템이 성공적으로 작동했습니다!")
        else:
            print("[WAVE] 데모를 종료합니다.")
    except EOFError:
        print("\n[INFO] 자동 데모를 실행합니다...")
        await demo_workflow()
        print("\n[PARTY] 데모 완료! 멀티에이전트 시스템이 성공적으로 작동했습니다!")

if __name__ == "__main__":
    asyncio.run(main())