import evdev 

key_map = {
    evdev.ecodes.KEY_RESERVED: 'reserved',
    evdev.ecodes.KEY_ESC: 'esc',
    evdev.ecodes.KEY_1: '1',
    evdev.ecodes.KEY_2: '2',
    evdev.ecodes.KEY_3: '3',
    evdev.ecodes.KEY_4: '4',
    evdev.ecodes.KEY_5: '5',
    evdev.ecodes.KEY_6: '6',
    evdev.ecodes.KEY_7: '7',
    evdev.ecodes.KEY_8: '8',
    evdev.ecodes.KEY_9: '9',
    evdev.ecodes.KEY_0: '0',
    evdev.ecodes.KEY_MINUS: 'minus',
    evdev.ecodes.KEY_EQUAL: 'equal',
    evdev.ecodes.KEY_BACKSPACE: 'backspace',
    evdev.ecodes.KEY_TAB: 'tab',
    evdev.ecodes.KEY_Q: 'q',
    evdev.ecodes.KEY_W: 'w',
    evdev.ecodes.KEY_E: 'e',
    evdev.ecodes.KEY_R: 'r',
    evdev.ecodes.KEY_T: 't',
    evdev.ecodes.KEY_Y: 'y',
    evdev.ecodes.KEY_U: 'u',
    evdev.ecodes.KEY_I: 'i',
    evdev.ecodes.KEY_O: 'o',
    evdev.ecodes.KEY_P: 'p',
    evdev.ecodes.KEY_LEFTBRACE: 'leftbrace',
    evdev.ecodes.KEY_RIGHTBRACE: 'rightbrace',
    evdev.ecodes.KEY_ENTER: 'enter',
    evdev.ecodes.KEY_LEFTCTRL: 'ctrlleft',
    evdev.ecodes.KEY_A: 'a',
    evdev.ecodes.KEY_S: 's',
    evdev.ecodes.KEY_D: 'd',
    evdev.ecodes.KEY_F: 'f',
    evdev.ecodes.KEY_G: 'g',
    evdev.ecodes.KEY_H: 'h',
    evdev.ecodes.KEY_J: 'j',
    evdev.ecodes.KEY_K: 'k',
    evdev.ecodes.KEY_L: 'l',
    evdev.ecodes.KEY_SEMICOLON: 'semicolon',
    evdev.ecodes.KEY_APOSTROPHE: 'apostrophe',
    evdev.ecodes.KEY_GRAVE: 'grave',
    evdev.ecodes.KEY_LEFTSHIFT: 'shiftleft',
    evdev.ecodes.KEY_BACKSLASH: 'backslash',
    evdev.ecodes.KEY_Z: 'z',
    evdev.ecodes.KEY_X: 'x',
    evdev.ecodes.KEY_C: 'c',
    evdev.ecodes.KEY_V: 'v',
    evdev.ecodes.KEY_B: 'b',
    evdev.ecodes.KEY_N: 'n',
    evdev.ecodes.KEY_M: 'm',
    evdev.ecodes.KEY_COMMA: 'comma',
    evdev.ecodes.KEY_DOT: 'dot',
    evdev.ecodes.KEY_SLASH: 'slash',
    evdev.ecodes.KEY_RIGHTSHIFT: 'shiftright',
    evdev.ecodes.KEY_KPASTERISK: 'asterisk',
    evdev.ecodes.KEY_LEFTALT: 'altleft',
    evdev.ecodes.KEY_SPACE: 'space',
    evdev.ecodes.KEY_CAPSLOCK: 'capslock',
    evdev.ecodes.KEY_F1: 'f1',
    evdev.ecodes.KEY_F2: 'f2',
    evdev.ecodes.KEY_F3: 'f3',
    evdev.ecodes.KEY_F4: 'f4',
    evdev.ecodes.KEY_F5: 'f5',
    evdev.ecodes.KEY_F6: 'f6',
    evdev.ecodes.KEY_F7: 'f7',
    evdev.ecodes.KEY_F8: 'f8',
    evdev.ecodes.KEY_F9: 'f9',
    evdev.ecodes.KEY_F10: 'f10',
    evdev.ecodes.KEY_NUMLOCK: 'numlock',
    evdev.ecodes.KEY_SCROLLLOCK: 'scrolllock',
    evdev.ecodes.KEY_KP7: 'numpad7',
    evdev.ecodes.KEY_KP8: 'numpad8',
    evdev.ecodes.KEY_KP9: 'numpad9',
    evdev.ecodes.KEY_KPMINUS: 'subtract',
    evdev.ecodes.KEY_KP4: 'numpad4',
    evdev.ecodes.KEY_KP5: 'numpad5',
    evdev.ecodes.KEY_KP6: 'numpad6',
    evdev.ecodes.KEY_KPPLUS: 'add',
    evdev.ecodes.KEY_KP1: 'numpad1',
    evdev.ecodes.KEY_KP2: 'numpad2',
    evdev.ecodes.KEY_KP3: 'numpad3',
    evdev.ecodes.KEY_KP0: 'numpad0',
    evdev.ecodes.KEY_KPDOT: 'decimal',
    evdev.ecodes.KEY_ZENKAKUHANKAKU: 'zenkakuhankaku',
    evdev.ecodes.KEY_102ND: '102nd',
    evdev.ecodes.KEY_F11: 'f11',
    evdev.ecodes.KEY_F12: 'f12',
    evdev.ecodes.KEY_RO: 'ro',
    evdev.ecodes.KEY_KATAKANA: 'katakana',
    evdev.ecodes.KEY_HIRAGANA: 'hiragana',
    evdev.ecodes.KEY_HENKAN: 'henkan',
    evdev.ecodes.KEY_KATAKANAHIRAGANA: 'katakanahiragana',
    evdev.ecodes.KEY_MUHENKAN: 'muhenkan',
    evdev.ecodes.KEY_KPJPCOMMA: 'jpcomma',
    evdev.ecodes.KEY_KPENTER: 'enter',
    evdev.ecodes.KEY_RIGHTCTRL: 'ctrlright',
    evdev.ecodes.KEY_KPSLASH: 'divide',
    evdev.ecodes.KEY_SYSRQ: 'sysrq',
    evdev.ecodes.KEY_RIGHTALT: 'altright',
    evdev.ecodes.KEY_LINEFEED: 'linefeed',
    evdev.ecodes.KEY_HOME: 'home',
    evdev.ecodes.KEY_UP: 'up',
    evdev.ecodes.KEY_PAGEUP: 'pageup',
    evdev.ecodes.KEY_LEFT: 'left',
    evdev.ecodes.KEY_RIGHT: 'right',
    evdev.ecodes.KEY_END: 'end',
    evdev.ecodes.KEY_DOWN: 'down',
    evdev.ecodes.KEY_PAGEDOWN: 'pagedown',
    evdev.ecodes.KEY_INSERT: 'insert',
    evdev.ecodes.KEY_DELETE: 'delete',
    evdev.ecodes.KEY_MACRO: 'macro',
    evdev.ecodes.KEY_MUTE: 'mute',
    evdev.ecodes.KEY_VOLUMEDOWN: 'volumedown',
    evdev.ecodes.KEY_VOLUMEUP: 'volumeup',
    evdev.ecodes.KEY_POWER: 'power',
    evdev.ecodes.KEY_KPEQUAL: 'equals',
    evdev.ecodes.KEY_KPPLUSMINUS: 'plusminus',
    evdev.ecodes.KEY_PAUSE: 'pause',
    evdev.ecodes.KEY_SCALE: 'scale',
    evdev.ecodes.KEY_KPCOMMA: 'comma',
    evdev.ecodes.KEY_HANGEUL: 'hangeul',
    evdev.ecodes.KEY_HANJA: 'hanja',
    evdev.ecodes.KEY_YEN: 'yen',
    evdev.ecodes.KEY_LEFTMETA: 'metaleft',
    evdev.ecodes.KEY_RIGHTMETA: 'metaright',
    evdev.ecodes.KEY_COMPOSE: 'compose',
    evdev.ecodes.KEY_STOP: 'stop',
    evdev.ecodes.KEY_AGAIN: 'again',
    evdev.ecodes.KEY_PROPS: 'props',
    evdev.ecodes.KEY_UNDO: 'undo',
    evdev.ecodes.KEY_FRONT: 'front',
    evdev.ecodes.KEY_COPY: 'copy',
    evdev.ecodes.KEY_OPEN: 'open',
    evdev.ecodes.KEY_PASTE: 'paste',
    evdev.ecodes.KEY_FIND: 'find',
    evdev.ecodes.KEY_CUT: 'cut',
    evdev.ecodes.KEY_HELP: 'help',
    evdev.ecodes.KEY_MENU: 'menu',
    evdev.ecodes.KEY_CALC: 'calculator',
    evdev.ecodes.KEY_SETUP: 'setup',
    evdev.ecodes.KEY_SLEEP: 'sleep',
    evdev.ecodes.KEY_WAKEUP: 'wakeup',
    evdev.ecodes.KEY_FILE: 'file',
    evdev.ecodes.KEY_SENDFILE: 'sendfile',
    evdev.ecodes.KEY_DELETEFILE: 'deletefile',
    evdev.ecodes.KEY_XFER: 'xfer',
    evdev.ecodes.KEY_PROG1: 'prog1',
    evdev.ecodes.KEY_PROG2: 'prog2',
    evdev.ecodes.KEY_WWW: 'www',
    evdev.ecodes.KEY_MSDOS: 'msdos',
    evdev.ecodes.KEY_COFFEE: 'coffee',
    evdev.ecodes.KEY_SCREENLOCK: 'screenlock',
    evdev.ecodes.KEY_ROTATE_DISPLAY: 'rotate_display',
    evdev.ecodes.KEY_DIRECTION: 'direction',
    evdev.ecodes.KEY_CYCLEWINDOWS: 'cyclewindows',
    evdev.ecodes.KEY_MAIL: 'mail',
    evdev.ecodes.KEY_BOOKMARKS: 'bookmarks',
    evdev.ecodes.KEY_COMPUTER: 'computer',
    evdev.ecodes.KEY_BACK: 'back',
    evdev.ecodes.KEY_FORWARD: 'forward',
    evdev.ecodes.KEY_CLOSECD: 'closecd',
    evdev.ecodes.KEY_EJECTCD: 'ejectcd',
    evdev.ecodes.KEY_EJECTCLOSECD: 'ejectclosecd',
    evdev.ecodes.KEY_NEXTSONG: 'nexttrack',
    evdev.ecodes.KEY_PLAYPAUSE: 'playpause',
    evdev.ecodes.KEY_PREVIOUSSONG: 'prevtrack',
    evdev.ecodes.KEY_STOPCD: 'stopcd',
    evdev.ecodes.KEY_RECORD: 'record',
    evdev.ecodes.KEY_REWIND: 'rewind',
    evdev.ecodes.KEY_PHONE: 'phone',
    evdev.ecodes.KEY_ISO: 'iso',
    evdev.ecodes.KEY_CONFIG: 'config',
    evdev.ecodes.KEY_HOMEPAGE: 'homepage',
    evdev.ecodes.KEY_REFRESH: 'refresh',
    evdev.ecodes.KEY_EXIT: 'exit',
    evdev.ecodes.KEY_MOVE: 'move',
    evdev.ecodes.KEY_EDIT: 'edit',
    evdev.ecodes.KEY_SCROLLUP: 'scrollup',
    evdev.ecodes.KEY_SCROLLDOWN: 'scrolldown',
    evdev.ecodes.KEY_KPLEFTPAREN: 'leftparen',
    evdev.ecodes.KEY_KPRIGHTPAREN: 'rightparen',
    evdev.ecodes.KEY_NEW: 'new',
    evdev.ecodes.KEY_REDO: 'redo',
    evdev.ecodes.KEY_F13: 'f13',
    evdev.ecodes.KEY_F14: 'f14',
    evdev.ecodes.KEY_F15: 'f15',
    evdev.ecodes.KEY_F16: 'f16',
    evdev.ecodes.KEY_F17: 'f17',
    evdev.ecodes.KEY_F18: 'f18',
    evdev.ecodes.KEY_F19: 'f19',
    evdev.ecodes.KEY_F20: 'f20',
    evdev.ecodes.KEY_F21: 'f21',
    evdev.ecodes.KEY_F22: 'f22',
    evdev.ecodes.KEY_F23: 'f23',
    evdev.ecodes.KEY_F24: 'f24',
    evdev.ecodes.KEY_PLAYCD: 'playcd',
    evdev.ecodes.KEY_PAUSECD: 'pausecd',
    evdev.ecodes.KEY_PROG3: 'prog3',
    evdev.ecodes.KEY_PROG4: 'prog4',
    evdev.ecodes.KEY_DASHBOARD: 'dashboard',
    evdev.ecodes.KEY_SUSPEND: 'suspend',
    evdev.ecodes.KEY_CLOSE: 'close',
    evdev.ecodes.KEY_PLAY: 'play',
    evdev.ecodes.KEY_FASTFORWARD: 'fastforward',
    evdev.ecodes.KEY_BASSBOOST: 'bassboost',
    evdev.ecodes.KEY_PRINT: 'print',
    evdev.ecodes.KEY_HP: 'hp',
    evdev.ecodes.KEY_CAMERA: 'camera',
    evdev.ecodes.KEY_SOUND: 'sound',
    evdev.ecodes.KEY_QUESTION: 'question',
    evdev.ecodes.KEY_EMAIL: 'email',
    evdev.ecodes.KEY_CHAT: 'chat',
    evdev.ecodes.KEY_SEARCH: 'search',
    evdev.ecodes.KEY_CONNECT: 'connect',
    evdev.ecodes.KEY_FINANCE: 'finance',
    evdev.ecodes.KEY_SPORT: 'sport',
    evdev.ecodes.KEY_SHOP: 'shop',
    evdev.ecodes.KEY_ALTERASE: 'alterase',
    evdev.ecodes.KEY_CANCEL: 'cancel',
    evdev.ecodes.KEY_BRIGHTNESSDOWN: 'brightnessdown',
    evdev.ecodes.KEY_BRIGHTNESSUP: 'brightnessup',
    evdev.ecodes.KEY_MEDIA: 'media',
    evdev.ecodes.KEY_SWITCHVIDEOMODE: 'switchvideomode',
    evdev.ecodes.KEY_KBDILLUMTOGGLE: 'kbdillumtoggle',
    evdev.ecodes.KEY_KBDILLUMDOWN: 'kbdillumdown',
    evdev.ecodes.KEY_KBDILLUMUP: 'kbdillumup',
    evdev.ecodes.KEY_SEND: 'send',
    evdev.ecodes.KEY_REPLY: 'reply',
    evdev.ecodes.KEY_FORWARDMAIL: 'forwardmail',
    evdev.ecodes.KEY_SAVE: 'save',
    evdev.ecodes.KEY_DOCUMENTS: 'documents',
    evdev.ecodes.KEY_BATTERY: 'battery',
    evdev.ecodes.KEY_BLUETOOTH: 'bluetooth',
    evdev.ecodes.KEY_WLAN: 'wlan',
    evdev.ecodes.KEY_UWB: 'uwb',
    evdev.ecodes.KEY_UNKNOWN: 'unknown',
    evdev.ecodes.KEY_VIDEO_NEXT: 'nextvideo',
    evdev.ecodes.KEY_VIDEO_PREV: 'prevvideo',
    evdev.ecodes.KEY_BRIGHTNESS_CYCLE: 'brightnesscycle',
    evdev.ecodes.KEY_BRIGHTNESS_AUTO: 'brightnessauto',
    evdev.ecodes.KEY_DISPLAY_OFF: 'displayoff',
    evdev.ecodes.KEY_WWAN: 'wwan',
    evdev.ecodes.KEY_RFKILL: 'rfkill',
    evdev.ecodes.KEY_MICMUTE: 'micmute',
}