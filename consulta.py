# -*- coding: utf-8 -*-

import uuid
from lxml import html
import re
from lxml.etree import tostring as htmlstring
import io
import json
import regex



class ConsultaCNPJ:
    """Crawller para o TJDF."""


    def __init__(self, *args, **kwargs):
        self._content = None
        self.processo={}

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = html.fromstring(value)

    def busca_por_cnpj(self):
        with open('tjDF.html', 'rb') as file:
            arquivo = file.read()
        self.content = arquivo

        self._get_processo()
        with io.open('data.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.processo, ensure_ascii=False))

    def _get_processo(self) -> None:

        xpath = '//hidden[@id="detalhamentoDeProcesso"]/span'
        linhas = [x.text_content().strip() for x in self.content.xpath(xpath)]
        vara_completa=[linhas[5], linhas[6]]
        feito_completo=[linhas[12], linhas[13]]

        self.processo['processo'] = {"circunscricao":linhas[1],
                                     "processo": linhas[2],
                                     "data_dist":linhas[3],
                                     "cnj":linhas[4],
                                     "preferencia_na_tramitacao":self._get_preferencia(),
                                     "vara":vara_completa,
                                     "natureza_da_vara":linhas[7],
                                     "endereco_vara":linhas[8],
                                     "horario_de_funcionamento":linhas[9],
                                     "classe":linhas[10],
                                     "assunto":linhas[11],
                                     "feito":feito_completo,
                                     "valor_da_causa":linhas[14],
                                     "requerente":self._get_requerente(),
                                     "advogado_reu":self._get_advogado_reu()
        }

        self.processo['partes'] = self._get_andamento_processo()


    def _get_preferencia(self):
        try:
            return self.content.xpath('//span[@id="i_preferenciaTramitacao"]/text()')[0].strip()
        except Exception as ex: # pylint: disable=unused-variable
            return None

    def _get_requerente(self):
        try:
            return self.content.xpath('//span[@id="i_nomeAutor"]/text()')[0].strip()
        except Exception as ex: # pylint: disable=unused-variable
            return None

    def _get_advogado_reu(self):
        try:
            return self.content.xpath('//span[@id="i_advogadoReu"]/text()')[0].strip()
        except Exception as ex: # pylint: disable=unused-variable
            return None

    def _get_andamento_processo(self):
        andamento_processo = []
        xpath = self.content.xpath('//span[@id="i_advogadoReu"]/following-sibling::hidden//tbody/tr')
        for element in xpath:
            andamento_processo.append(self._get_dados_andamento(element))
        return andamento_processo


    def _get_dados_andamento(self, element) -> None:

        dados_andamento = {"data":self._get_data(element),
                       "andamento":self._get_andamento(element),
                       "complemento":self._get_complemento(element)}
        return dados_andamento


    def _get_data(self,element) -> str:
        try:
           return element.xpath('td[1]//span/text()')[0].strip()
        except Exception as ex: # pylint: disable=unused-variable
            return None

    def _get_andamento(self,element) -> str:
        try:
            return element.xpath('td[2]//span/text()')[0].strip()
        except Exception as ex: # pylint: disable=unused-variable
            return None

    def _get_complemento(self,element) -> str:
        try:
            return self.tratar_complementos_aspas(element)
        except Exception as ex: # pylint: disable=unused-variable
            return None

    def tratar_complementos_aspas(self, element) -> str:  #está função serve para extrair o dado do primeiro complemento.
        elemento = element.xpath('td[3]/font/text()')[0].strip()
        search = regex.search(r".+", elemento)
        if not search:
            return element.xpath('td[3]/a/font/text()')
        else:
            return elemento


if __name__ == '__main__':



    print('##### Iniciando Busca #######')

    ConsultaCNPJ().busca_por_cnpj()
    print('##### Busca Encerrada #######')

