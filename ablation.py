from enum import auto, Enum
import CAI

class AblationSetting(Enum):
    """
    [S1] Direct LLM translation                : WITH_E2NL=False,   WITH_VERIFIER=False,    WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S2]  + E2NL (human review + intervention) : WITH_E2NL=True,    WITH_VERIFIER=False,    WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S3] Verifier loops                        : WITH_E2NL=False,   WITH_VERIFIER=True,     WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S4]  + E2NL (human review + intervention) : WITH_E2NL=True,    WITH_VERIFIER=True,     WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S5] Decomposition (no human)              : WITH_E2NL=False,   WITH_VERIFIER=True,     WITH_DECOMP=True,     WITH_DECOMP_CONFIRM=False, 
    [S6]  + human review + intervention        : WITH_E2NL=False,   WITH_VERIFIER=True,     WITH_DECOMP=True,     WITH_DECOMP_CONFIRM=True, 
    [S7]  + E2NL (human review + intervention) : WITH_E2NL=True,    WITH_VERIFIER=True,     WITH_DECOMP=True,     WITH_DECOMP_CONFIRM=True, 
    """
    #                   WITH_E2NL,    WITH_VERIFIER,    WITH_DECOMP,    WITH_DECOMP_CONFIRM
    DIRECT =            (False,       False,            False,          False)
    DIRECT_E2NL =       (True,        False,            False,          False)
    VERIFIER =          (False,       True,             False,          False)
    VERIFIER_E2NL =     (True,        True,             False,          False)
    DECOMP =            (False,       True,             True,           False)
    DECOMP_CONFIRM =    (False,       True,             True,           True)
    DECOMP_E2NL =       (True,        True,             True,           True)
    
    def apply(setting):
        CAI.WITH_E2NL, CAI.WITH_VERIFIER, CAI.WITH_DECOMP, CAI.WITH_DECOMP_CONFIRM = setting.value
        CAI.SETTING_NAME = setting.name