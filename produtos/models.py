# produtos/models.py

from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    data_compra = models.DateField()
    data_validade = models.DateField()
    quantidade = models.IntegerField()

    def __str__(self):
        return self.nome
