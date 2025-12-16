from __future__ import annotations

from pydantic import BaseModel, Field


class ReferencedFile(BaseModel):
    path: str
    importCount: int = Field(ge=0)


class UnusedImport(BaseModel):
    file: str
    importSource: str
    importedNames: list[str] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    directory: str
    roots: list[str] | None = None
    includeExtensions: list[str] | None = None


class AnalysisResult(BaseModel):
    referencedFiles: list[ReferencedFile]
    unreferencedFiles: list[str]
    unusedImports: list[UnusedImport]
    experimentalUnusefulFiles: list[str] = Field(default_factory=list, alias="__experimentalUnusefulFiles")
    warnings: list[str] = Field(default_factory=list)

    experimentalNotice: str = Field(
        default="`__experimentalUnusefulFiles` 是实验性属性，非常不稳定，仅供参考。",
        alias="__experimentalNotice",
    )

    model_config = {
        "populate_by_name": True,
    }
