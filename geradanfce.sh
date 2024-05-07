#!/bin/bash

url="http://localhost:8000/geradanfce"

gera_danfce() {
    if [ -z "$1" ]; then
        echo "Erro: Forneça o caminho do arquivo como parâmetro."
        return 1
    fi

    arquivo=$1

    if [[ "$arquivo" == *".json" ]]; then
        curl -X POST \
            -H "Content-Type: application/json" \
            -d @"$arquivo" "$url" -o danfce.txt
    else
        conteudo=$(cat "$arquivo")
        json_data="{\"xml_content\": $(jq -sR '.' <<< "$conteudo")}"
        curl -X POST \
            -H "Content-Type: application/json" \
            -d "$json_data" "$url" -o danfce.txt
    fi
}


gera_danfce "$1"
