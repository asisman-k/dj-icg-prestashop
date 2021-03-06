from django.contrib import admin

# Register your models here.
from .models import *
from . import prestashop, controller

class ManufacturerAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['icg_id', 'icg_name', 'ps_id', 'ps_name', 'modified_date', 'updated']
    list_display = ['icg_id', 'icg_name', 'ps_id', 'ps_name', 'modified_date', 'updated']
    readonly_fields = ['modified_date']
    search_fields = ['icg_id', 'icg_name', 'ps_id', 'ps_name']
    list_filter = ['updated']

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_manufacturer(obj)

admin.site.register(Manufacturer, ManufacturerAdmin)

class CategoryAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['ps_id', 'ps_name', 'ps_parent', 'ps_position','ps_active','created_date', 'modified_date', 'updated']
    list_display = ['ps_id', 'ps_name', 'ps_parent', 'ps_position','ps_active','created_date', 'modified_date', 'updated']
    readonly_fields = ['created_date','modified_date']
    search_fields = ['ps_id', 'ps_name']
    list_filter = ['updated']

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_category(obj)

admin.site.register(Category, CategoryAdmin)

class CombinationAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS", "createStock"]
    fields = ['ps_id','icg_talla','icg_color','product_id','ean13','discontinued', 'updated']
    list_display = ['ps_id', 'product_id','icg_talla','icg_color','ean13','discontinued', 'product_icg_modified_date', 'created_date', 'modified_date', 'updated']
    search_fields = ['product_id__icg_reference', 'product_id__icg_name','icg_talla','icg_color','ean13']
    list_filter = ['discontinued', 'updated']

    def product_icg_modified_date(self, instance):
        if instance.product_id:
            return instance.product_id.icg_modified_date
        else:
            return 'NO_DATE'

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_combination(obj)

    def createStock(self, request, queryset):
        c = controller.ControllerICGProducts()
        for obj in queryset:
            stock = c.get_create_or_update('Stock', {'combination_id': obj},{})

admin.site.register(Combination, CombinationAdmin)


class PriceAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['ps_id', 'combination_id', 'pvp_siva','iva','pvp','icg_modified_date',  'created_date', 'modified_date', 'updated']
    readonly_fields = ['combination_id', 'icg_modified_date', 'modified_date', 'created_date']
    list_display = ['ps_id', 'combination_id','pvp_siva','iva','pvp', 'discontinued', 'icg_modified_date',  'created_date', 'modified_date', 'updated']
    search_fields = ['combination_id__product_id__icg_reference', 'combination_id__icg_talla', 'combination_id__icg_color']
    list_filter = ['updated', 'icg_modified_date', 'iva']

    def discontinued(self, instance):
        if instance.combination_id:
            return instance.combination_id.discontinued
        else:
            return 'NsNc'

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_price(obj)


admin.site.register(Price, PriceAdmin)


class StockAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['ps_id', 'combination_id', 'icg_stock', 'ps_stock', 'icg_modified_date', 'updated']
    list_display = ['ps_id', 'combination_id', 'product_icg_id', 'icg_stock', 'ps_stock', 'discontinued', 'icg_modified_date', 'created_date', 'modified_date', 'updated']
    readonly_fields = ['combination_id', 'icg_modified_date']
    search_fields = ['combination_id__product_id__icg_reference', 'combination_id__icg_talla', 'combination_id__icg_color', 'icg_modified_date']
    list_filter = ['updated', 'icg_modified_date', 'modified_date']

    def product_icg_id(self, instance):
        if instance.combination_id:
            return instance.combination_id.product_id.icg_id
        else:
            return 'NO_PS_ID'

    def discontinued(self, instance):
        if instance.combination_id:
            return instance.combination_id.discontinued
        else:
            return 'NsNc'

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #TODO
            #p.tryToUpdateProduct_fromPS(obj)
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_stock(obj)

admin.site.register(Stock, StockAdmin)


class ProductOptionAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['product_id', 'ps_id','ps_name', 'ps_icg_type', 'ps_public_name', 'updated']
    list_display = ['ps_id','ps_name', 'product_id','ps_icg_type', 'ps_group_type', 'ps_public_name', 'ps_iscolor', 'created_date', 'modified_date', 'updated']
    search_fields = ['product_id__icg_reference', 'product_id__icg_name', 'ps_id','ps_name', 'ps_icg_type', 'ps_public_name']
    list_filter = ['ps_icg_type', 'updated', 'ps_iscolor']

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #TODO
            #p.tryToUpdateProduct_fromPS(obj)
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_product_options(obj)

admin.site.register(ProductOption, ProductOptionAdmin)


class ProductOptionValueAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fiels = ['po_id', 'ps_id','ps_name', 'icg_name']
    list_display = ['po_id', 'ps_id','ps_name', 'icg_name', 'created_date', 'modified_date', 'updated']
    search_fields = ['po_id__product_id__icg_reference', 'ps_id','ps_name', 'icg_name']
    list_filter = ['po_id__ps_icg_type', 'updated']

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_product_option_value(obj)

admin.site.register(ProductOptionValue, ProductOptionValueAdmin)


class SpecificPriceAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fiels = ['ps_id', 'product_id', 'combination_id', 'dto_percent', 'icg_modified_date', 'modified_date']
    readonly_fields = ['combination_id', 'icg_modified_date', 'modified_date']
    list_display = ['ps_id', 'product_id','combination_id','ps_combination_id', 'dto_percent','ps_reduction', 'icg_modified_date', 'created_date', 'modified_date', 'updated']
    search_fields = ['combination_id__product_id__icg_reference', 'product_id__icg_name', 'ps_id']
    list_filter = ['updated', 'dto_percent', 'icg_modified_date']

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_specific_price(obj)

admin.site.register(SpecificPrice, SpecificPriceAdmin)


class ProductesPrestashop(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name', 'iva', 'modified_date',
            'icg_modified_date', 'visible_web', 'manufacturer', 'manufacturer_name', 'updated']
    readonly_fields = ['manufacturer_name', 'icg_modified_date', 'modified_date']
    list_display = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name', 'iva', 'visible_web',
            'manufacturer_name', 'created_date', 'modified_date', 'icg_modified_date', 'updated']
    search_fields = ['ps_id', 'icg_reference', 'icg_name', 'ps_name', 'manufacturer__icg_name']
    list_filter = ['visible_web', 'updated', 'manufacturer__icg_name', 'iva']

    def manufacturer_name(self, instance):
        if instance.manufacturer:
            return instance.manufacturer.ps_name
        else:
            return 'NO_NAME'

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            p.tryToUpdateProduct_fromPS(obj)

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_product(obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(ProductesPrestashop, self).get_readonly_fields(request, obj)
        if obj:
            return readonly_fields + ['icg_id', 'icg_name']
        return readonly_fields

admin.site.register(Product, ProductesPrestashop)


class TranslationProductAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['lang','prod', 'ps_name', 'ps_description', 'ps_description_short','created_date', 'modified_date']
    list_display = ['lang', 'prod', 'ps_name', 'ps_description', 'ps_description_short','created_date', 'modified_date']
    readonly_fields = ['created_date','modified_date']
    search_fields = ['lang','prod', 'ps_name']
    list_filter = ['lang']

    def baixar_de_PS(self, request, queryset):
        return True

    def pujar_cap_a_PS(self, request, queryset):
        return True

admin.site.register(TranslationProduct, TranslationProductAdmin)

class TranslationProductOptionAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['lang','po', 'ps_name', 'ps_public_name', 'created_date', 'modified_date']
    list_display = ['lang', 'po', 'ps_name', 'ps_public_name', 'created_date', 'modified_date']
    readonly_fields = ['created_date','modified_date']
    search_fields = ['lang','po', 'ps_name']
    list_filter = ['lang']

    def baixar_de_PS(self, request, queryset):
        return True

    def pujar_cap_a_PS(self, request, queryset):
        return True

admin.site.register(TranslationProductOption, TranslationProductOptionAdmin)

class TranslationProductOptionValueAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['lang','pov', 'ps_name','created_date', 'modified_date']
    list_display = ['lang', 'pov', 'ps_name', 'created_date', 'modified_date']
    readonly_fields = ['created_date','modified_date']
    search_fields = ['lang','pov', 'ps_name']
    list_filter = ['lang']

    def baixar_de_PS(self, request, queryset):
        return True

    def pujar_cap_a_PS(self, request, queryset):
        return True

admin.site.register(TranslationProductOptionValue, TranslationProductOptionValueAdmin)

class TranslationCategoryAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['lang','cat', 'ps_name', 'ps_link_rewrite','ps_description',
        'ps_meta_description','ps_meta_keywords','ps_meta_title','created_date', 'modified_date']
    list_display = ['lang', 'cat', 'ps_name', 'ps_link_rewrite','ps_description',
        'ps_meta_description','ps_meta_keywords','ps_meta_title','created_date', 'modified_date']
    readonly_fields = ['created_date','modified_date']
    search_fields = ['lang','cat', 'ps_name']
    list_filter = ['lang']

    def baixar_de_PS(self, request, queryset):
        return True

    def pujar_cap_a_PS(self, request, queryset):
        return True

admin.site.register(TranslationCategory, TranslationCategoryAdmin)

class ImageAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['ps_id', 'ps_img_type', 'ps_resource','ps_url','image','created_date', 'modified_date']
    list_display = ['ps_id', 'ps_img_type', 'ps_resource','ps_url','image','created_date', 'modified_date']
    readonly_fields = ['created_date','modified_date']
    search_fields = ['ps_id','ps_url']
    list_filter = ['ps_img_type', 'ps_resource']

    def baixar_de_PS(self, request, queryset):
        return True

    def pujar_cap_a_PS(self, request, queryset):
        return True

admin.site.register(Image, ImageAdmin)

