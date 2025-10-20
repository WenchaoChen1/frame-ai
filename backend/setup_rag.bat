@echo off
echo ========================================
echo RAG 功能安装脚本
echo ========================================
echo.

echo [1/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [2/4] 安装 RAG 依赖包...
pip install elasticsearch pgvector sentence-transformers pypdf python-docx pdfplumber rank-bm25 faiss-cpu langchain-community langchain-elasticsearch unstructured jieba

echo.
echo [3/4] 测试模块导入...
python -c "from app.models.knowledge_base import KnowledgeBase; print('✓ 知识库模型导入成功')"
if %ERRORLEVEL% NEQ 0 (
    echo ✗ 模块导入失败
    pause
    exit /b 1
)

echo.
echo [4/4] 运行数据库迁移...
python migrations\run_migration_005.py
if %ERRORLEVEL% NEQ 0 (
    echo ✗ 数据库迁移失败，请检查数据库连接
    echo 提示：确保 PostgreSQL 正在运行，并已启用 vector 扩展
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ RAG 功能安装完成！
echo ========================================
echo.
echo 现在可以启动应用：
echo   python -m app.main
echo.
echo 或者访问：
echo   http://localhost:8000/docs
echo.
pause

