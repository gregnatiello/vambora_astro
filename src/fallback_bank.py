"""
fallback_bank.py
Banco de conteúdo pré-escrito usado quando a IA não está configurada
(modo --test, ausência de OPENAI_API_KEY, ou falha da API).

Isso garante que o pipeline SEMPRE produza um pacote completo — o item 31
do briefing pede explicitamente para nunca gerar um post quebrado.

Cada entrada já segue as regras de tom do briefing: informal, debochado,
frases curtas, sem termos técnicos de astrologia, sem generalidades de
horóscopo tradicional.
"""

FALLBACK_SETS = {
    "Traição": {
        "carousel_title": "TOP 5 SIGNOS QUE MAIS TRAEM",
        "subtitle": "E ainda conseguem fazer você se sentir culpado",
        "signs": [
            {"sign": "Gêmeos", "text": "Gêmeos não trai por maldade. Trai porque surgiu uma conversa boa e ele simplesmente esqueceu que tinha compromisso.\n\nDepois explica tão bem que você quase pede desculpa por ter duvidado."},
            {"sign": "Sagitário", "text": "Sagitário jura que \"é só amizade\".\n\nA amizade é que sempre mora longe, some no story junto e nunca é apresentada pra ninguém."},
            {"sign": "Leão", "text": "Leão não esconde. Ele só \"esquece\" de contar.\n\nQuando descobre que foi pego, o problema nunca é o que ele fez — é como você reagiu."},
            {"sign": "Áries", "text": "Áries não planeja trair. Mas se a oportunidade bater na porta, ele nem finge que pensou duas vezes.\n\nDepois quer resolver tudo em uma conversa de cinco minutos."},
            {"sign": "Peixes", "text": "Peixes trai no imaginário há meses antes de trair de verdade.\n\nQuando finalmente acontece, ainda chora mais que a própria vítima."},
        ],
    },
    "Término": {
        "carousel_title": "TOP 5 SIGNOS QUE TERMINAM E VOLTAM",
        "subtitle": "Como se nada tivesse acontecido",
        "signs": [
            {"sign": "Câncer", "text": "Câncer termina no calor da emoção.\n\nDuas horas depois já está mandando áudio de sete minutos implorando pra conversar."},
            {"sign": "Escorpião", "text": "Escorpião termina em silêncio, sem post, sem escândalo.\n\nSó pra voltar semanas depois como se o intervalo nunca tivesse existido."},
            {"sign": "Touro", "text": "Touro demora uma eternidade pra terminar.\n\nMas quando termina mesmo, some por dois dias e volta agindo como se fosse só um desentendimento bobo."},
            {"sign": "Libra", "text": "Libra termina, pesa os prós e contras, e três dias depois já achou um motivo lógico pra reatar."},
            {"sign": "Peixes", "text": "Peixes nunca termina de verdade. Ele só dá um tempo pra sentir mais saudade ainda."},
        ],
    },
    "Ciúmes": {
        "carousel_title": "TOP 5 SIGNOS MAIS CIUMENTOS",
        "subtitle": "Só que eles juram que é \"zelo\"",
        "signs": [
            {"sign": "Escorpião", "text": "Escorpião não pergunta quem curtiu a foto. Ele já sabe, já investigou e já tem uma teoria da conspiração pronta."},
            {"sign": "Câncer", "text": "Câncer não fala que ficou com ciúme. Ele só fica quieto, muda o tom da voz e some do assunto por três horas."},
            {"sign": "Touro", "text": "Touro é tranquilo até aparecer alguém \"curtindo\" o que é dele.\n\nAí a paciência lendária vira memória."},
            {"sign": "Leão", "text": "Leão não tem ciúme. Ele tem \"orgulho ferido\" — que na prática é a mesma coisa, só que com mais drama."},
            {"sign": "Áries", "text": "Áries sente ciúme e resolve na hora, sem filtro, sem pensar duas vezes.\n\nDepois se pergunta por que a treta cresceu tão rápido."},
        ],
    },
    "Discussões": {
        "carousel_title": "TOP 5 SIGNOS QUE NÃO SABEM PERDER UMA DISCUSSÃO",
        "subtitle": "Mesmo quando já perderam há dez minutos",
        "signs": [
            {"sign": "Áries", "text": "Áries não quer discutir. Quer ganhar.\n\nSe perceber que está perdendo, muda de assunto, aumenta o tom e ainda sai achando que venceu."},
            {"sign": "Escorpião", "text": "Escorpião discute com calma assustadora.\n\nO problema é que ele guarda cada argumento seu pra usar contra você meses depois."},
            {"sign": "Leão", "text": "Leão pode até estar errado. Só que admitir isso em público não está no repertório dele."},
            {"sign": "Sagitário", "text": "Sagitário discute e no meio da briga ainda solta uma piada.\n\nVocê fica sem saber se ri ou continua bravo."},
            {"sign": "Capricórnio", "text": "Capricórnio não grita. Ele te vence com fatos, dados e uma linha do tempo cronológica do seu erro."},
        ],
    },
    "Ostentação": {
        "carousel_title": "TOP 5 SIGNOS QUE GASTARIAM TUDO SÓ PRA MANTER AS APARÊNCIAS",
        "subtitle": "Salário some, status permanece",
        "signs": [
            {"sign": "Leão", "text": "Leão fala que não liga pra opinião dos outros.\n\nMas escolhe o restaurante pensando exatamente na opinião dos outros."},
            {"sign": "Libra", "text": "Libra parcela em doze vezes, mas parcela com estilo.\n\nPra ele, aparência também é investimento."},
            {"sign": "Touro", "text": "Touro fala que dinheiro não traz felicidade.\n\nMas fica feliz mesmo é vendo o saldo da conta — e gastando ele todo em conforto."},
            {"sign": "Sagitário", "text": "Sagitário gasta a viagem inteira do mês em uma única saída de fim de semana.\n\nDepois vive de story e de saudade."},
            {"sign": "Áries", "text": "Áries decide na hora, compra na hora e só vai pensar no cartão de crédito depois."},
        ],
    },
    "Relacionamentos": {
        "carousel_title": "TOP 5 SIGNOS QUE SÃO PERIGO EM UM RELACIONAMENTO",
        "subtitle": "E ainda juram que são \"fáceis de lidar\"",
        "signs": [
            {"sign": "Escorpião", "text": "Escorpião ama intensamente e desconfia na mesma intensidade.\n\nCom ele não existe meio-termo, só \"tudo\" ou \"nada\"."},
            {"sign": "Gêmeos", "text": "Gêmeos muda de humor três vezes no mesmo dia.\n\nVocê nunca sabe qual versão vai chegar em casa."},
            {"sign": "Leão", "text": "Leão precisa ser prioridade o tempo todo.\n\nSe sentir que dividiu atenção, o clima muda na hora."},
            {"sign": "Câncer", "text": "Câncer leva tudo pro lado pessoal, inclusive coisas que nem eram sobre ele."},
            {"sign": "Capricórnio", "text": "Capricórnio coloca trabalho na frente de tudo e só percebe o preço disso quando já é tarde."},
        ],
    },
}

DEFAULT_CATEGORY = "Relacionamentos"


def get_fallback_set(category: str) -> dict:
    return FALLBACK_SETS.get(category, FALLBACK_SETS[DEFAULT_CATEGORY])
