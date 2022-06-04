import codecs
import csv

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product


fs = FileSystemStorage(location='tmp/')


# Serializer
class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


# Viewset
class ProductViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['POST'])
    def upload_data(self, request):
        """Upload data from CSV"""
        file = request.FILES["file"]

        content = file.read()  # these are bytes
        file_content = ContentFile(content)
        file_name = fs.save(
            "_tmp.csv", file_content
        )
        tmp_file = fs.path(file_name)

        csv_file = open(tmp_file, errors="ignore")
        reader = csv.reader(csv_file)
        next(reader)
        
        product_list = []
        for id_, row in enumerate(reader):
            (
                user,
                category,
                price,
                name,
                description,
                quantity
            ) = row
            product_list.append(
                Product(
                    user=user,
                    category=category,
                    price=price,
                    name=name,
                    description=description,
                    quantity=quantity,
                )
            )

        Product.objects.bulk_create(product_list)

        return Response("Successfully upload the data")

    @action(detail=False, methods=['POST'])
    def upload_data_with_validation(self, request):
        """Upload data from CSV, with validation."""
        file = request.FILES.get("file")

        reader = csv.DictReader(codecs.iterdecode(file, "utf-8"), delimiter=",")
        data = list(reader)

        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        product_list = []
        for row in serializer.data:
            product_list.append(
                Product(
                    user_id=row["user"],
                    category=row["category"],
                    price=row["price"],
                    name=row["name"],
                    description=row["description"],
                    quantity=row["quantity"],
                )
            )

        Product.objects.bulk_create(product_list)

        return Response("Successfully upload the data")