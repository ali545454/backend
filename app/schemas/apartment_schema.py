from marshmallow import Schema, fields

# تعريف مخطط (Schema) لتحويل بيانات الشقق إلى JSON والعكس
class ApartmentSchema(Schema):
    """
    Schema for serializing and deserializing Apartment objects.
    """
    id = fields.Int(dump_only=True)
    uuid = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    price = fields.Float(required=True)
    area = fields.Float()
    bedrooms = fields.Int()
    bathrooms = fields.Int()
    kitchens = fields.Int()
    floorNumber = fields.Int()
    address = fields.Str()
    neighborhood = fields.Str()
    residenceType = fields.Str()
    totalBeds = fields.Int()
    availableBeds = fields.Int()
    features = fields.List(fields.Str())
    main_image = fields.Str()
    
    # حقول للقراءة فقط (يتم التحكم بها من الخادم)
    isVerified = fields.Bool(dump_only=True)
    rating = fields.Float(dump_only=True)
    reviewCount = fields.Int(dump_only=True)
    
    # هذا الحقل يفترض وجود علاقة اسمها 'owner' في موديل الشقة
    # ويعرض اسم المالك بالكامل
    ownerName = fields.Str(attribute="owner.full_name", dump_only=True)
    
    # هذا الحقل يعتمد على المستخدم الحالي، لذا يكون للقراءة فقط في المخطط العام
    isFavorite = fields.Bool(dump_only=True)
