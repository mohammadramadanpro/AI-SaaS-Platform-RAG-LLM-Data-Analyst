"""Data analyst endpoints — upload CSV/Excel, ask questions, get charts."""

import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import Dataset, get_db, generate_id
from ..models.schemas import AnalystQueryRequest, AnalystQueryResponse, DatasetResponse
from ..services import llm
from ..services.code_executor import execute_code, extract_code_block, get_data_summary

router = APIRouter(prefix="/api/analyst", tags=["Data Analyst"])

CODE_GEN_SYSTEM = """You are a Python data analyst. Write Python code using a pandas DataFrame called `df` to answer the user's question.

Rules:
- Use only: pandas, numpy, plotly.express (as px), plotly.graph_objects (as go)
- Store the final answer in a variable called `result`
- If a chart is needed, create it with plotly and save: `fig.write_html(f"{charts_dir}/chart.html")`
  then set `chart_path = f"{charts_dir}/chart.html"`
- Do NOT use print, open, os, subprocess, sys, or any system modules
- Return ONLY Python code inside a ```python``` block"""

MAX_RETRIES = 2


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile,
    user_id: str = "demo_user",
    db: AsyncSession = Depends(get_db),
):
    fname = file.filename.lower()
    if not fname.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(400, "Only CSV and Excel files are accepted")

    content = await file.read()
    if len(content) > settings.MAX_CSV_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large (max {settings.MAX_CSV_SIZE_MB}MB)")

    dataset_id = generate_id()
    ds_dir = settings.DATA_DIR / "users" / user_id / "datasets"
    ds_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix
    file_path = ds_dir / f"{dataset_id}{ext}"
    file_path.write_bytes(content)

    try:
        if ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        file_path.unlink()
        raise HTTPException(400, f"Failed to parse file: {e}")

    columns = list(df.columns)
    ds = Dataset(
        id=dataset_id,
        user_id=user_id,
        filename=file.filename,
        row_count=len(df),
        col_count=len(columns),
        columns_json=json.dumps(columns),
    )
    db.add(ds)
    await db.commit()

    return DatasetResponse(
        id=dataset_id,
        filename=file.filename,
        row_count=len(df),
        col_count=len(columns),
        columns=columns,
    )


@router.get("/datasets", response_model=list[DatasetResponse])
async def list_datasets(
    user_id: str = "demo_user",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dataset).where(Dataset.user_id == user_id)
    )
    datasets = result.scalars().all()
    return [
        DatasetResponse(
            id=d.id,
            filename=d.filename,
            row_count=d.row_count,
            col_count=d.col_count,
            columns=json.loads(d.columns_json),
        )
        for d in datasets
    ]


@router.post("/query", response_model=AnalystQueryResponse)
async def query_dataset(
    req: AnalystQueryRequest,
    user_id: str = "demo_user",
    db: AsyncSession = Depends(get_db),
):
    # Load dataset
    result = await db.execute(
        select(Dataset).where(Dataset.id == req.dataset_id, Dataset.user_id == user_id)
    )
    ds = result.scalar_one_or_none()
    if not ds:
        raise HTTPException(404, "Dataset not found")

    ds_dir = settings.DATA_DIR / "users" / user_id / "datasets"
    # Find file by ID prefix
    files = list(ds_dir.glob(f"{req.dataset_id}.*"))
    if not files:
        raise HTTPException(404, "Dataset file not found")

    file_path = files[0]
    if file_path.suffix == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    data_summary = get_data_summary(df)

    # Charts directory
    charts_dir = settings.DATA_DIR / "users" / user_id / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        prompt = f"""{data_summary}

User question: {req.question}"""
        if last_error:
            prompt += f"\n\nPrevious attempt failed with: {last_error}\nFix the code:"

        prompt += "\n\nPython code:"

        code_response = await llm.generate(prompt, system=CODE_GEN_SYSTEM)
        code = extract_code_block(code_response)
        result = execute_code(code, df, str(charts_dir))

        if "error" not in result:
            chart_url = None
            if result.get("chart"):
                chart_url = f"/api/analyst/chart/{user_id}/{Path(result['chart']).name}"
            return AnalystQueryResponse(
                answer=result["result"], chart_url=chart_url
            )
        last_error = result["error"]

    return AnalystQueryResponse(
        answer="", error=f"Failed after {MAX_RETRIES + 1} attempts: {last_error}"
    )


@router.get("/chart/{user_id}/{filename}")
async def get_chart(user_id: str, filename: str):
    chart_path = settings.DATA_DIR / "users" / user_id / "charts" / filename
    if not chart_path.exists():
        raise HTTPException(404, "Chart not found")
    return FileResponse(str(chart_path), media_type="text/html")
