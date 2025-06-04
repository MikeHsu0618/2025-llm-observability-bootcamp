# 匯入必要的函式庫
from google.adk.agents.sequential_agent import SequentialAgent  # 匯入循序代理
from google.adk.agents import Agent  # 匯入基礎代理類別
from google.genai import types  # 匯入型別定義
from google.adk.sessions import InMemorySessionService  # 匯入記憶體會話服務
from google.adk.runners import Runner  # 匯入執行器
from google.adk.tools import FunctionTool  # 匯入函式工具，用於建立自訂工具
import openlit
import os

# Initialize openlit
openlit.init(
    otlp_endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', 
                                 'http://host.docker.internal:4318'),
    application_name='code_optimizer',
    environment='dev'
    )


APP_NAME = "code_pipeline_app"
USER_ID = "dev_user_01"
SESSION_ID = "pipeline_session_01"
GEMINI_MODEL = "gemini-2.0-flash-exp"

code_writer_agent = Agent(
    name="CodeWriterAgent",
    model=GEMINI_MODEL,
    instruction="""你是一個程式碼編寫 AI。
    根據使用者的請求，編寫初始 Python 程式碼。
    只輸出原始程式碼區塊。
    """,
    description="根據規格說明編寫初始程式碼。",
    output_key="generated_code"
)

code_reviewer_agent = Agent(
    name="CodeReviewerAgent",
    model=GEMINI_MODEL,
    instruction="""你是一個程式碼審查 AI。
    審查會話狀態中索引鍵名為 'generated_code' 的 Python 程式碼。
    提供關於潛在錯誤、風格問題或改進的建設性回饋。
    注重清晰度和正確性。
    僅輸出審查評論。
    """,
    description="審查程式碼並提供回饋。",
    output_key="review_comments"
)

code_refactorer_agent = Agent(
    name="CodeRefactorerAgent",
    model=GEMINI_MODEL,
    instruction="""你是一個程式碼重構 AI。
    取得會話狀態索引鍵 'generated_code' 中的原始 Python 程式碼
    以及會話狀態索引鍵 'review_comments' 中的審查評論。
    重構原始程式碼以解決回饋並提高其品質。
    僅輸出最終的、重構後的程式碼區塊。
    """,
    description="根據審查評論重構程式碼。",
    output_key="refactored_code"
)

code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent]
)

root_agent = Agent(
    name="CodeAssistant",
    model=GEMINI_MODEL,
    instruction="""你是一個程式碼助理 AI。
    你的角色是透過三步管線幫助使用者改進程式碼：
    1. 根據規格說明編寫初始程式碼
    2. 審查程式碼以發現問題和改進
    3. 根據審查回饋重構程式碼

    當使用者請求程式碼協助時，使用 code_pipeline_agent 來處理請求。
    將最終的、重構後的程式碼作為你的回應呈現給使用者。
    """,
    description="透過編寫-審查-重構管線改進程式碼的助理。",
    tools=[],
    sub_agents=[code_pipeline_agent]
)

