

def readClientServerVersion():
  try: 
    from account_shared import readClientServerVersion
    return readClientServerVersion()
  
  except ImportError:
    from version_utils import readClientServerVersion
    from helpers import clientVersionGetter
    from constants import AUTH_REALM
    req, ver = readClientServerVersion(clientVersionGetter)
    if len(ver.split('#')) == 2: ver = ver.split('#')[0]
    
    
    prefix = ''
    
    try:
      from realm import CURRENT_REALM, IS_CT
      if CURRENT_REALM == 'RU' and IS_CT: prefix = 'rpt_'
      if CURRENT_REALM == 'RU' and not IS_CT: prefix = 'ru_'
    except ImportError:
      pass   
    
    if AUTH_REALM == 'CT' and prefix == '': prefix = 'ct_'
    return (req, prefix + ver)

def getBattleLogShellTypesNames():
  from constants import BATTLE_LOG_SHELL_TYPES

  BATTLE_LOG_SHELL_TYPES_NAMES = {
    BATTLE_LOG_SHELL_TYPES.HOLLOW_CHARGE: 'HOLLOW_CHARGE',
    BATTLE_LOG_SHELL_TYPES.HOLLOW_CHARGE: 'HOLLOW_CHARGE',
    BATTLE_LOG_SHELL_TYPES.ARMOR_PIERCING: 'ARMOR_PIERCING',
    BATTLE_LOG_SHELL_TYPES.ARMOR_PIERCING_HE: 'ARMOR_PIERCING_HE',
    BATTLE_LOG_SHELL_TYPES.ARMOR_PIERCING_CR: 'ARMOR_PIERCING_CR',
    BATTLE_LOG_SHELL_TYPES.SMOKE: 'SMOKE',
    BATTLE_LOG_SHELL_TYPES.HE_MODERN: 'HE_MODERN',
    BATTLE_LOG_SHELL_TYPES.HE_LEGACY_STUN: 'HE_LEGACY_STUN',
    BATTLE_LOG_SHELL_TYPES.HE_LEGACY_NO_STUN: 'HE_LEGACY_NO_STUN',
  }
  
  try: BATTLE_LOG_SHELL_TYPES_NAMES[BATTLE_LOG_SHELL_TYPES.FLAME] = 'FLAME'
  except: pass
  
  return BATTLE_LOG_SHELL_TYPES_NAMES