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


# --- 常數定義 ---
APP_NAME = "code_pipeline_app"  # 應用程式名稱
USER_ID = "dev_user_01"  # 使用者 ID
SESSION_ID = "pipeline_session_01"  # 會話 ID
GEMINI_MODEL = "gemini-2.0-flash-exp"  # 使用的 Gemini 模型

# --- 1. 定義程式碼處理管線的各個階段子代理 ---
# 程式碼編寫代理
# 接收初始規格說明（來自使用者查詢）並編寫程式碼
code_writer_agent = Agent(
    name="CodeWriterAgent",  # 代理名稱
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一個程式碼編寫 AI。
    根據使用者的請求，編寫初始 Python 程式碼。
    只輸出原始程式碼區塊。
    """,  # 代理指令（中文版）
    description="根據規格說明編寫初始程式碼。",  # 代理描述
    # 將其輸出（產生的程式碼）儲存到會話狀態中
    # 索引鍵名為 'generated_code'
    output_key="generated_code"  # 輸出索引鍵，用於儲存代理輸出到會話狀態
)

# 程式碼審查代理
# 讀取上一個代理產生的程式碼（從狀態中讀取）並提供回饋
code_reviewer_agent = Agent(
    name="CodeReviewerAgent",  # 代理名稱
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一個程式碼審查 AI。
    審查會話狀態中索引鍵名為 'generated_code' 的 Python 程式碼。
    提供關於潛在錯誤、風格問題或改進的建設性回饋。
    注重清晰度和正確性。
    僅輸出審查評論。
    """,  # 代理指令（中文版）
    description="審查程式碼並提供回饋。",  # 代理描述
    # 將其輸出（審查評論）儲存到會話狀態中
    # 索引鍵名為 'review_comments'
    output_key="review_comments"  # 輸出索引鍵，用於儲存代理輸出到會話狀態
)

# 程式碼重構代理
# 取得原始程式碼和審查評論（從狀態中讀取）並重構程式碼
code_refactorer_agent = Agent(
    name="CodeRefactorerAgent",  # 代理名稱
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一個程式碼重構 AI。
    取得會話狀態索引鍵 'generated_code' 中的原始 Python 程式碼
    以及會話狀態索引鍵 'review_comments' 中的審查評論。
    重構原始程式碼以解決回饋並提高其品質。
    僅輸出最終的、重構後的程式碼區塊。
    """,  # 代理指令（中文版）
    description="根據審查評論重構程式碼。",  # 代理描述
    # 將其輸出（重構的程式碼）儲存到會話狀態中
    # 索引鍵名為 'refactored_code'
    output_key="refactored_code"  # 輸出索引鍵，用於儲存代理輸出到會話狀態
)

# --- 2. 建立循序代理 ---
# 這個代理透過按順序執行子代理來編排管線
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",  # 循序代理名稱
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent]
    # 子代理將按提供的順序執行：編寫器 -> 審查器 -> 重構器
)

# --- 3. 建立一個函式作為工具 ---
def process_code_request(request: str) -> str:
    """
    使用程式碼處理管線處理使用者的程式碼請求。

    Args:
        request (str): 使用者的程式碼請求，如「建立一個計算加法的函式」

    Returns:
        str: 處理後的最終程式碼
    """
    print(f"處理程式碼請求: {request}")
    # 這個函式實際上不會被執行，而是被 LLM 用來理解它應該如何使用 code_pipeline_agent
    # 真正的執行是透過 root_agent 對 code_pipeline_agent 的委派實現的
    return "最終的程式碼將在這裡返回"

# --- 4. 建立根代理 ---
root_agent = Agent(
    name="CodeAssistant",  # 根代理名稱
    model=GEMINI_MODEL,  # 使用的模型
    instruction="""你是一個程式碼助理 AI。
    你的角色是透過三步管線幫助使用者改進程式碼：
    1. 根據規格說明編寫初始程式碼
    2. 審查程式碼以發現問題和改進
    3. 根據審查回饋重構程式碼

    當使用者請求程式碼協助時，使用 code_pipeline_agent 來處理請求。
    將最終的、重構後的程式碼作為你的回應呈現給使用者。
    """,  # 根代理指令（中文版）
    description="透過編寫-審查-重構管線改進程式碼的助理。",  # 根代理描述
    # 不在工具中新增 code_pipeline_agent，而是作為子代理
    tools=[],  # 這裡可以為空，或者新增其他工具
    sub_agents=[code_pipeline_agent]  # 將 code_pipeline_agent 作為子代理
)

