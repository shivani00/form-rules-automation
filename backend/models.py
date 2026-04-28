from pydantic import BaseModel, Field
from typing import List, Optional


# ---------- STATE ----------
class State(BaseModel):
    stateCd: str
    stateName: str


# ---------- CONDITION ----------
class Condition(BaseModel):
    attributeName: str
    oid: str  # 🔥 mandatory
    value: str
    operator: Optional[str] = "="
    logic: Optional[str] = "AND"


# ---------- THEN ----------
class ThenAction(BaseModel):
    action: str
    value: str


# ---------- FORM ----------
class FormDetails(BaseModel):
    objectName: Optional[str] = None
    formTitle: Optional[str] = None
    formShortName: Optional[str] = None
    formType: Optional[str] = None

    # 🔥 additional fields (already aligned with UI)
    workstream: Optional[str] = None
    printHandlingTypeCode: Optional[str] = None
    reprintOnChange: Optional[str] = None
    policyTab: Optional[str] = None
    pullListIndicator: Optional[str] = None
    singleTermForm: Optional[str] = None
    toBeRationalizedDate: Optional[str] = None
    rationalizedDate: Optional[str] = None
    rationalizationPriority: Optional[str] = None
    fillInAttribute: Optional[str] = None
    notes: Optional[str] = None
    expired: Optional[str] = None
    requestor: Optional[str] = None
    requestDate: Optional[str] = None


# ---------- MAIN RULE ----------
class Rule(BaseModel):
    ruleType: str

    # ----- FOR -----
    workstream: Optional[str] = None
    businessUnit: Optional[str] = None
    rollupGroups: Optional[str] = None
    subGroups: Optional[str] = None
    productType: Optional[str] = None

    # ----- STATES -----
    states: List[State] = Field(default_factory=list)  # 🔥 FIXED

    stateType: Optional[str] = None

    # ----- TRANSACTION -----
    transactions: Optional[str] = None
    user: Optional[str] = None

    # ----- DATES -----
    effectiveIRID: Optional[str] = None
    implementation: Optional[str] = None
    effectiveDate: Optional[str] = None
    expirationIRID: Optional[str] = None
    implementationDate: Optional[str] = None
    expirationDate: Optional[str] = None

    # ----- LOGIC -----
    conditions: List[Condition] = Field(default_factory=list)  # 🔥 FIXED
    thenActions: List[ThenAction] = Field(default_factory=list)  # 🔥 FIXED

    # ----- FORM -----
    form: Optional[FormDetails] = None


# ---------- OSARI ----------
class OsariMapping(BaseModel):
    objectId: str
    objectName: str
    pathType: str
    auto: bool
    cmp: bool
    umb: bool
    wc: bool
    context: str
    effectiveVersion: Optional[str] = None
    expiryVersion: Optional[str] = None
    entity: str
    attribute: Optional[str] = None
    path: str
    pathNotes: Optional[str] = None
    lastUpdated: Optional[str] = None
    stereotype: Optional[bool] = False