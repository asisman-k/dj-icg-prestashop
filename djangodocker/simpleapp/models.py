# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from . import mytools, mssql, constants
import csv
from django.utils.timezone import make_aware
from datetime import datetime

class Manufacturer(models.Model):
    """
    docstring here
        :param models.Model:
    """
    icg_id = models.IntegerField()
    icg_name = models.CharField(max_length=100)
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, blank=True, default="")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated = models.BooleanField(default=True)
    fields_updated = models.CharField(max_length=100, default="{}")

    class Meta:
        verbose_name = 'manufacturer'
        verbose_name_plural = 'manufacturers'


    def saved_in_prestashop(self):
        return ps_id

    def __str__(self):
        return (str(self.pk) + ": " + str(self.icg_id ) + " > " + self.icg_name + " > " + str(self.ps_id) + " > " + self.ps_name)

    def compareICG(self, man):
        result = {}
        if self.icg_name != man.icg_name:
            result['icg_name'] = man.icg_name
        return result

    def compare(self, man):
        if self.icg_name != man['manufacturer']['name']:
            man['manufacturer']['name'] = self.icg_name
            return True, man
        return False, {}

    @classmethod
    def createFromPS(cls, man_dict):
        man = cls(icg_id=0, icg_name = '',
             ps_name = man_dict['manufacturer']['name'],
             ps_id = man_dict['manufacturer']['id'])
        return man


class Product(models.Model):
    icg_id = models.IntegerField(unique=True, blank=True, null=True)
    icg_reference = models.CharField(max_length=20)
    icg_name = models.CharField(max_length=100)
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, default='')
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.DO_NOTHING, null=True)
    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=True)
    visible_web = models.BooleanField(default=True)
    fields_updated = models.CharField(max_length=200, default="{}")

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return "Producte %d de nom %s i referencia %s" % (self.icg_id, self.icg_name, self.icg_reference)

    def saved_in_prestashop(self):
        return ps_id

    @classmethod
    def create(cls, icg_id, icg_reference, icg_name, manufacturer):
        product = cls(icg_id=icg_id, icg_reference=icg_reference,
            icg_name=icg_name, manufacturer=manufacturer)
        return product

    @classmethod
    def createFromPS(cls, product_dict):
        prod = cls(icg_id=0, icg_reference = product_dict['product']['reference'],
             ps_name = mytools.get_ps_language(product_dict['product']['name']['language']),
             ps_id = product_dict['product']['id'])
        return prod

    def compareICG(self, product):
        result = {}
        if product.icg_name and (self.icg_name != product.icg_name):
            result['icg_name'] = product.icg_name
        if product.icg_reference and (self.icg_reference != product.icg_reference):
            result['icg_reference'] = product.icg_reference
        if product.manufacturer and  (self.manufacturer != product.manufacturer):
            result['manufacturer'] = product.manufacturer
        if self.visible_web != product.visible_web:
            result['visible_web'] = "0"
        if product.icg_modified_date and (self.icg_modified_date != product.icg_modified_date):
            result['icg_modified_date'] = product.icg_modified_date
        return result

    def compare(self, product):
        result = {}
        if hasattr(product, 'icg_id'):
            if self.icg_reference != product.icg_reference:
                result['icg_reference'] = product.icg_reference
            if self.manufacturer != product.manufacturer:
                result['manufacturer'] = str(product.manufacturer.icg_id)
            if self.icg_name != product.icg_name:
                result['icg_name'] = product.icg_name
            if self.visible_web != product.visible_web:
                result['visible_web'] = "0"
        elif isinstance(product, dict):
            modified = False
            if self.icg_reference and (str(self.icg_reference) != str(product['product']['reference'])):
                product['product']['reference'] = self.icg_reference
                modified = True
            if self.manufacturer and (str(self.manufacturer.ps_id) != str(product['product']['id_manufacturer'])):
                product['product']['id_manufacturer'] = str(self.manufacturer.ps_id)
                modified = True
            if self.icg_name and (self.icg_name != mytools.get_ps_language(
                product['product']['name']['language'])):
                #TODO: more than one language
                mytools.update_ps_language(product['product']['name']['language'], self.icg_name)
                modified = True
            if self.visible_web != True if product['product']['active'] == 1 else False:
                product['product']['active'] = 1 if self.visible_web else 0
                modified = True
            return modified, product

        return result

    def compareOldWith(self, man):
        #Example amb control amb idiomes
        print(man)
        changed = False
        man['manufacturer'].pop('link_rewrite', None)
        if self.icg_name != mytools.get_ps_language(man['manufacturer']['name']):
            man['manufacturer']['name'] = mytools.get_ps_language(
                man['manufacturer']['name'], self.icg_name)
            changed = True
        print(man)
        return changed, man

    def updateFromICG(self):
        ms = mssql.MSSQL()
        result = ms.getProductData(constants.URLBASE, self.icg_reference, self.icg_id)
        if isinstance(result, bool):
            return False
        updated = dict()
        for index,row in result.iterrows():
            updated['icg_id'] = row[0]
            updated['icg_reference'] = row[1]
            updated['icg_name'] = row[6]
            updated['icg_modified_date'] = make_aware(datetime.strptime(row[11], '%Y-%m-%d %H:%M:%S'))
            updated['updated'] = True
            Product.objects.filter(icg_id=row[0]).update(**updated)
        return True


class Combination(models.Model):
    ps_id = models.IntegerField(blank=True, null=True) #previous ps_product_attribut
    icg_talla = models.CharField(max_length=15, blank=True)
    icg_color = models.CharField(max_length=15, blank=True)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    ean13 = models.CharField(max_length=15, blank=True)
    minimal_quantity = models.IntegerField(default=1)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    updated = models.BooleanField(default=True)
    discontinued = models.BooleanField(default=False) #descatalogado
    fields_updated = models.CharField(max_length=200, default="{}")

    class Meta:
        verbose_name = 'combination'
        verbose_name_plural = 'combinations'

    def __str__(self):
        return "Combinació del Producte %s de color %s i talla %s" % (
            str(self.product_id.icg_id), self.icg_color, self.icg_talla)

    @classmethod
    def createFromPS(cls, comb_dict, product):
        comb = cls(ps_id = comb_dict['combination']['id'],
            ean13 = comb_dict['combination']['ean13'],
            product_id = product)
        return comb

    def saved_in_prestashop(self):
        return ps_id

    def compare(self, comb):
        modified = False
        if self.ean13 != str(comb['combination']['ean13']):
            comb['combination']['ean13'] = self.ean13
            modified = True
        if self.discontinued:
            comb['discontinued'] = True
            modified = True
        return modified, comb

    def compareICG(self, comb):
        result = {}
        if self.ean13 != comb.ean13:
            result['ean13'] = comb.ean13
        if self.discontinued != comb.discontinued:
            result['discontinued'] = comb.discontinued
        return result

    def updateFromICG(self):
        ms = mssql.MSSQL()
        result = ms.getCombinationData(constants.URLBASE, self.product_id.icg_reference,
            self.icg_talla, self.icg_color)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            self.ean13 = row[4]
            self.discontinued = True if row[15] == 'T' else False
            self.updated = True
            self.save()
        return True

class Stock(models.Model):
    ps_id = models.IntegerField(blank=True, null=True) #stock_availables
    combination_id = models.OneToOneField('Combination', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    icg_stock = models.IntegerField(default=0)
    ps_stock = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=False)
    fields_updated = models.CharField(max_length=200, default="{}")

    class Meta:
        verbose_name = 'stock'
        verbose_name_plural = 'stocks'

    @classmethod
    def createFromPS(cls, stock_dict, product, combination):
        stock = cls(ps_id = stock_dict['stock_available']['id'],
            ps_stock = stock_dict['stock_available']['quantity'],
            combination_id = combination, product_id = product)
        return stock

    def compareICG(self, stock):
        result = {}
        if self.icg_stock != stock.icg_stock:
            result['icg_stock'] = stock.icg_stock
        return result

    def updateFromICG(self):
        ms = mssql.MSSQL()
        result = ms.getStockData(constants.URLBASE, self.combination_id.product_id.icg_id,
            self.combination_id.icg_talla, self.combination_id.icg_color)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            self.icg_stock = row[7]
            self.icg_modified_date = make_aware(datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S'))
            self.updated = True
            self.save()
        return True

class Price(models.Model):
    combination_id = models.OneToOneField('Combination', on_delete=models.CASCADE, primary_key=True)
    ps_id = models.IntegerField(default=0)
    pvp = models.FloatField(default=0)
    preu_oferta = models.FloatField(default=0)
    iva = models.IntegerField(default=0)
    pvp_siva = models.FloatField(default=0)
    preu_oferta_siva = models.FloatField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=True)
    fields_updated = models.CharField(max_length=200, default="{}")

    class Meta:
        verbose_name = 'price'
        verbose_name_plural = 'prices'

    @classmethod
    def createFromPS(cls, price_dict, combination):
        price = cls(ps_id = price_dict['combination']['id'],
            pvp_siva = float(price_dict['combination']['price']),
            combination_id = combination)
        return price

    def compare(self, product):
        result = {}
        if self.iva != product.iva:
            result['iva'] = product.iva
        if self.pvp_siva != product.pvp_siva:
            result['pvp_siva'] = product.pvp_siva
        return result

    def compareICG(self, price):
        result = {}
        if self.iva != price.iva:
            result['iva'] = price.iva
        if self.pvp_siva != price.pvp_siva:
            result['pvp_siva'] = price.pvp_siva
        return result

    def updateFromICG(self):
        ms = mssql.MSSQL()
        result = ms.getPriceData(constants.URLBASE, self.combination_id.product_id.icg_id,
            self.combination_id.icg_talla, self.combination_id.icg_color)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            self.iva = row[8]
            self.pvp_siva = row[9]
            self.icg_modified_date = make_aware(datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S'))
            self.pvp = row[4]
            self.preu_oferta = float(row[4]) - float(row[7])
            self.preu_oferta = row[10]
            self.updated = True
            self.save()
        return True

class ProductOption(models.Model):
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, default='', unique=True)
    ps_icg_type = models.CharField(max_length=10, default='') #talla o color
    ps_public_name = models.CharField(max_length=100, default='')
    ps_group_type = models.CharField(max_length=15, default='')
    ps_position = models.IntegerField(default=0)
    ps_iscolor = models.BooleanField(default=False)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    updated = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'product_option'
        verbose_name_plural = 'products_options'

    @classmethod
    def create(cls, ps_name, product):
        ps_icg_type = ps_name.split('_')[1]
        po = cls(ps_name = ps_name, ps_icg_type = ps_icg_type, product_id = product)
        return po

    @classmethod
    def createFromPS(cls, po_dict, product):
        ps_name = mytools.get_ps_language(po_dict['product_option']['name']['language'])
        ps_icg_type = ps_name.split('_')[1]
        po = cls(ps_id = po_dict['product_option']['id'], ps_name = ps_name,
            ps_icg_type = ps_icg_type, product_id = product)
        return po

    def __str__(self):
        return "Producte combinacio %d del producte amb ref %s i de nom  %s" % (
            self.ps_id, self.product_id.icg_reference, self.ps_name)

    def saved_in_prestashop(self):
        return ps_id

    def compareICG(self, po):
        return {}

class ProductOptionValue(models.Model):
    icg_name = models.CharField(max_length=15, default='')
    ps_id = models.IntegerField(blank=True, null=True, default=0)
    ps_name = models.CharField(max_length=100, default='')
    po_id = models.ForeignKey('ProductOption', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    updated = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'product_option_value'
        verbose_name_plural = 'products_options_values'

    def __str__(self):
        return "Atribut %s del grup %s" % (self.icg_name, self.po_id.ps_name)

    @classmethod
    def createFromPS(cls, pov_dict, product_option):
        ps_name = mytools.get_ps_language(pov_dict['product_option_value']['name']['language'])
        pov = cls(ps_id = pov_dict['product_option_value']['id'], ps_name = ps_name,
            po_id = product_option)
        return pov

    def saved_in_prestashop(self):
        return ps_id

    def compareICG(self, po):
        return {}

class SpecificPrice(models.Model):
    ps_id = models.IntegerField(default=0)
    ps_reduction = models.FloatField(default=0)
    combination_id = models.OneToOneField('Combination', on_delete=models.CASCADE, null=True)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    dto_percent = models.IntegerField(default=0)
    dto_euros = models.FloatField(default=0)
    dto_euros_siva = models.FloatField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    icg_modified_date = models.DateTimeField(blank=True, null=True)
    updated = models.BooleanField(default=True)
    fields_updated = models.CharField(max_length=200, default="{}")

    class Meta:
        verbose_name = 'specific_price'
        verbose_name_plural = 'specific_prices'

    @classmethod
    def createFromPS(cls, sp_dict, product):
        price = cls(ps_id = sp_dict['specific_price']['id'],
            dto_percent = float(sp_dict['specific_price']['reduction']) * 100,
            product_id = product)
        return price

    def compare(self, product):
        result = {}
        if self.dto_percent != product.dto_percent:
            result['dto_percent'] = product.dto_percent
        return result

    def comparePS(self, product):
        if self.dto_percent != float(product['specific_price']['reduction']) * 100:
            product['specific_price']['reduction'] = str(float(self.dto_percent/100))
            return True, product
        return False, {}

    def compareICG(self, specific_price):
        result = {}
        if self.dto_percent != specific_price.dto_percent:
            result['dto_percent'] = specific_price.dto_percent
        return result

    def updateFromICG(self):
        ms = mssql.MSSQL()
        result = ms.getDiscountData(constants.URLBASE, self.product_id.icg_id)
        if isinstance(result, bool):
            return False
        for index,row in result.iterrows():
            self.dto_percent = row[5]
            self.icg_modified_date = make_aware(datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S'))
            self.updated = True
            self.save()
        return True

# vim: et ts=4 sw=4
