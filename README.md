# PyPrinter

Servidor Flask para conversão de xml do Documento Auxiliar da Nota Fiscal Eletrônica - Consumidor Eletrônico ou só DANFCE, 
para arquivos binários de impressão direta em modo texto em impressoras térmicas de 80mm.

<img src="https://raw.githubusercontent.com/cleitonleonel/PyPrinter/master/src/media/python-coupon.png" alt="PyPrinter" width="250"/>

## Clonando o projeto:

```shell
git clone https://github.com/cleitonleonel/PyPrinter.git
```

## Uso:
```shell
cd PyPrinter
pip install -r requirements.txt
python server.py
```

## Gerando danfce:
```shell
./geradanfce.sh ./docs/32210534971421000262650010000011211121100000-nfce.xml
```

## Imprimindo via lpr no Linux:
```shell
lpr -P nome_de_compartilhamento_da_impressora -o raw danfce.txt
```

# Este projeto ajudou você?

Se esse projeto deixar você ficar à vontade para fazer uma doação =), pode ser R $ 0,50 hahahaha. Para isso, basta ler o qrcode abaixo, ele foi gerado com meu outro projeto chamado [Pypix](https://github.com/cleitonleonel/pypix.git) arquivo de amostra.

<img src="https://github.com/cleitonleonel/pypix/blob/master/qrcode.png?raw=true" alt="Your image title" width="250"/>

# Desenvolvido por:

Cleiton Leonel Creton ==> cleiton.leonel@gmail.com
