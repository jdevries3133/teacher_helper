def MANUAL_FIXES(name):
    """
    Manual fixes for individual students. This is in the gitignore because
    it contains individual names
    """
    zoom_name_to_government_name = {
        'layla j': 'Layla Johnson',
        'derek r.': 'Derek Yu',
        'neljohn': 'Neljohn Frias',
        'redd': 'Raymond Redd',
        'a r d e n': 'Arden Ababio',
        'suheily nieves': 'Suheily Padilla',
        'pito azer': 'Philopateer Azer',
        'rina azer': 'Marina Azer',
        'ethanhoward': 'Ethan Howard',
        '𝙠𝙧𝙞𝙨𝙝': 'Krish Mehta',
        'atharva.zutshi': 'Atharva Zutshi',
        'nevaeh4a': 'Nevaeh Hill',
        'dashawm': 'Dashawn',
        'sakthi4a': 'Sakthi',
        'mohameddiatta': 'Mohamed Diatta',
        'dorienne': 'Dorienne Ruth Anne',
        'stanthemotoman': 'William Castillo',
        'ĉ̵̅̓̕h̴̛͈́͊l̷͒͐̿͒o̶̓̇̀̚e̶͂̀': 'Chloe Pfeifer',
        'brendy.valentina': 'Brendy Rivera',
        'miyah': 'Miya Madayag',
        'malachi': 'Malachi Tucker',
        'francine': 'Francine Garino',
        'darius': 'Darius Maximus Montecastro',
    }
    for k, v in zoom_name_to_government_name.items():
        if k in name:
            return v
    return name
