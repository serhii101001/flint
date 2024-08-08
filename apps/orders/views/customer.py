from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema_view, OpenApiResponse, extend_schema
from orders.enums import OrderStatus
from orders.exceptions import InsufficientBalanceException
from orders.models import Order
from orders.serializers import OrderSerializer


@extend_schema_view(
    get=extend_schema(
        summary="List of a users orders",
        description="List all orders for",
        responses={
            200: OrderSerializer(many=True),
            403: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Customer Orders"],
    ),
    post=extend_schema(
        summary="Create an order",
        description="Create an order for the user",
        responses={
            201: OrderSerializer(),
            400: OpenApiResponse(description="Bad Request"),
            403: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Customer Orders"],
    ),
)
class OrderListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.select_related("restaurant", "user")
            .prefetch_related("items", "items__product")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context


@extend_schema_view(
    post=extend_schema(
        summary="Pay for an order",
        description="Pay for an order",
        responses={
            200: OrderSerializer(),
            400: OpenApiResponse(description="Bad Request"),
            403: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Customer Orders"],
    ),
)
class OrderPayView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(
            Order,
            uuid=self.kwargs["uuid"],
            user=self.request.user,
            status=OrderStatus.PENDING_PAYMENT,
        )

    def post(self, request, uuid):
        order = self.get_object(uuid)
        try:
            order.status = OrderStatus.PROCESSING
            order.save()
            return Response({"message": "Order is being processed"}, status=status.HTTP_200_OK)

        except InsufficientBalanceException:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
