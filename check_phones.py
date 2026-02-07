"""
Script para verificar qué números de teléfono NO están registrados
"""
import sys
import io
from database import SessionLocal
import models

# Configurar salida UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Lista de números a verificar
phones_to_check = [
    "3057938318",
    "3126731714",
    "3117532838",
    "3154253977",
    "3164342204",
    "3173499441",
    "3214475140",
    "3137632065",
    "3194773483",
    "3172968793",
    "3134637195",
    "3148504288",
    "3025109312",
    "3107019994",
    "3196229645",
    "3187889858",
    "3213098850",
    "3185271722",
    "3137717077",
    "3209032108",
    "3053138733",
    "3123683613",
    "3112899220",
    "3108048869",
    "3125184110",
    "3022353563",
    "3145045191",
    "3003724046",
    "3192251960",
    "3103156960",
    "3204346868",
    "3132401209",
    "3107137882",
    "3222817259",
    "3117186217",
    "3155222119",
    "3123250311",
    "3223591592",
    "3155290906",
    "3194029676",
    "3002257517",
    "3125613865",
    "3102521459",
    "3174241484",
    "3045399021",
    "3172207155",
    "3103331086",
    "3174115945",
    "3028097029",
    "3118808921",
    "3173580920",
    "3168758943",
    "3192587329",
    "3163433088",
    "3113109859",
    "3053478612",
    "3146358728",
    "3105937102",
    "3004016415",
    "3005010549",
    "3155381037",
    "3212931225",
    "3112060931",
    "3133395566",
    "3154550205",
    "3202655287",
    "3102409461",
    "3153137381",
    "3134192399",
    "3212125258",
    "3167188836",
    "3115580217"
]

db = SessionLocal()

try:
    print(f"Verificando {len(phones_to_check)} números de teléfono...\n")

    registered = []
    not_registered = []

    for phone in phones_to_check:
        # Buscar usuario con este teléfono
        user = db.query(models.User).filter(models.User.phone == phone).first()

        if user:
            registered.append((phone, user.name, user.email))
        else:
            not_registered.append(phone)

    print(f"{'='*70}")
    print(f"RESULTADOS")
    print(f"{'='*70}")
    print(f"Total verificados: {len(phones_to_check)}")
    print(f"Registrados: {len(registered)}")
    print(f"NO registrados: {len(not_registered)}")
    print(f"{'='*70}\n")

    if not_registered:
        print(f"NÚMEROS NO REGISTRADOS ({len(not_registered)}):")
        print(f"{'-'*70}")
        for phone in not_registered:
            print(f"  {phone}")
    else:
        print("Todos los números están registrados!")

    if registered:
        print(f"\n\nNÚMEROS REGISTRADOS ({len(registered)}):")
        print(f"{'-'*70}")
        for phone, name, email in registered:
            print(f"  {phone} - {name} ({email})")

except Exception as e:
    print(f"X Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
