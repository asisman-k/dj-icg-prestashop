# -*- coding: utf-8 -*-
import prestapyt
from . import models, mssql
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.utils.timezone import now
from datetime import datetime
import logging

class ControllerICGProducts(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)


    def get_create_or_update(self, obj_name, primary_key, other_fields):
        dj_object = getattr(models, obj_name)
        create = dict(primary_key, **other_fields)
        m_new = dj_object(**create)
        try:
            m_old = dj_object.objects.get(**primary_key)
            updated = m_old.compareICG(m_new)
            if updated:
                updated['fields_updated'] = updated.copy()
                updated['updated'] = True
                updated['modified_date'] = now()
                dj_object.objects.filter(pk=m_old.pk).update(**updated)
                self.logger.info("Objecte '%s' modificada: %s", str(dj_object), str(updated))
            return m_old
        except ObjectDoesNotExist:
            m_new.save()
            self.logger.info("Objecte creada %s", str(dj_object))
            return m_new
        except MultipleObjectsReturned:
            self.logger.error("Objecte torna més d'un: %s", +
                str(dj_object.objects.filter(**primary_key)))

    def saveNewProducts(self, url_base=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newProducts(url_base)
        for index,row in np.iterrows():
            icg_id = row[0]
            icg_reference = row[1]
            icg_talla = row[2]
            icg_color = row[3]
            ean13 = row[4]
            icg_name = row[6].encode('utf-8')
            iva = row[8]
            #icg_modified_date = row[11]
            visible_web = True if row[12] == 'T' else False
            manufacturer_id = row[13]
            discontinued = True if row[15] == 'T' else False
            
            man = self.get_create_or_update('Manufacturer', 
                {'icg_id': manufacturer_id}, {'icg_name': row[14] })

            prod = self.get_create_or_update('Product', {'icg_id': icg_id},
                {'icg_reference': icg_reference, 'icg_name': icg_name,
                'visible_web': visible_web, 'manufacturer': man}) 

            comb = self.get_create_or_update('Combination', {'product_id': prod,
                'icg_color': icg_color, 'icg_talla': icg_talla},
                {'discontinued': discontinued, 'ean13': ean13})


class ControllerICGPrices(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)


    def get_create_or_update_product(self, icg_id):
        return models.Product.objects.get(icg_id = icg_id)


    def get_create_or_update_combination(self, product_id, icg_color, icg_talla):
        return models.Combination.objects.get(product_id = product_id, icg_color = str(icg_color),
             icg_talla = str(icg_talla))


    def get_create_or_update_price(self, combination_id, dto_percent, iva, pvp_siva):
        comb = None
        pc_new = models.Price(combination_id = combination_id, dto_percent = dto_percent,
            iva = iva, pvp_siva=pvp_siva)

        try:
            pc_old = models.Price.objects.get(combination_id = combination_id)
            updated = pc_old.compare(pc_new)
            if updated:
                models.Price.objects.filter(pk=pc_old.pk).update(**updated)
                self.logger.info("Preu modificat: %s", str(updated))
            comb = pc_old
        except ObjectDoesNotExist:
            self.logger.error("Preu creat: %s ", str(combination_id))
            pc_new.save()
            comb = pc_new
        except MultipleObjectsReturned:
            self.logger.error("Preu torna més d'un: %s",
                str(models.Price.objects.filter(combination_id = combination_id)))
            raise MultipleObjectsReturned(e)

        return comb


    def saveNewPrices(self, url_base=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np  = ms.newPrices(url_base)
        for index,row in np.iterrows():
            icg_id = eval(row[1])
            icg_talla = row[2].strip('\"')
            icg_color = row[3].strip('\"')
            dto_percent = eval(row[5])
            iva = eval(row[8])
            pvp_siva = eval(row[9])
            #icg_modified_date = row[12]

            prod = self.get_create_or_update_product(icg_id)
            comb = self.get_create_or_update_combination(prod, icg_color, icg_talla)
            comb2 = self.get_create_or_update_price(comb, dto_percent, iva, pvp_siva)



class ControllerICGStocks(object):
    def __init__(self, url_base=''):
        self._url_base = url_base
        self.logger = logging.getLogger(__name__)


    def get_create_or_update_product(self, icg_id):
        return models.Product.objects.get(icg_id = icg_id)


    def get_create_or_update_combination(self, product_id, icg_color, icg_talla):
        return models.Combination.objects.get(product_id = product_id, icg_color = str(icg_color),
             icg_talla = str(icg_talla))


    def get_create_or_update_stock(self, combination_id, icg_stock):
        stock = None
        try:
            stock = models.Stock.objects.get(combination_id = combination_id)
            self.logger.info("Stock modificat de %d: %s", combination_id.pk, str(icg_stock))
            stock.icg_stock = icg_stock
            stock.save()
        except ObjectDoesNotExist:
            stock = models.Stock(combination_id = combination_id, icg_stock = icg_stock)
            self.logger.error("Stock creat: %s ", str(combination_id))
            stock.save()
        except MultipleObjectsReturned as e:
            self.logger.error("Stock torna més d'un: %s",
                str(models.Price.objects.filter(combination_id = combination_id)))
            raise MultipleObjectsReturned(e)

        return stock


    def saveNewStocks(self, url_base=None):
        if not url_base:
            url_base = self._url_base
        ms = mssql.MSSQL()
        np = ms.newStocks(url_base)
        for index,row in np.iterrows():
            icg_id = eval(row[0])
            icg_talla = row[1].strip('\"')
            icg_color = row[2].strip('\"')
            icg_stock = eval(row[7])
            #icg_modified_date = row[8]

            prod = self.get_create_or_update_product(icg_id)
            comb = self.get_create_or_update_combination(prod, icg_color, icg_talla)
            comb2 = self.get_create_or_update_stock(comb, icg_stock)

# vim: et ts=4 sw=4
