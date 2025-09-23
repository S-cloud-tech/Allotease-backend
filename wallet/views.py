from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from main.models import Ticket
from .models import *
from . import serializers
import requests
import json

class WalletInfoViewSet(viewsets.ModelViewSet):
    queryset = Virtual_account.objects.all()
    serializer_class = serializers.WalletSerializer



class DepositFunds(APIView):

    def post(self, request):
        serializer = serializers.DepositSerializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        resp = serializer.save()
        return Response(resp)

class VerifyDeposit(APIView):

    def get(self, request, reference):
        transaction = Transaction.objects.get(
        paystack_payment_reference=reference, wallet__user=request.user)
        reference = transaction.paystack_payment_reference
        url = 'https://api.paystack.co/transaction/verify/{}'.format(reference)
        headers = {
            {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}}
        r = requests.get(url, headers=headers)
        resp = r.json()
        if resp['data']['status'] == 'success':
            status = resp['data']['status']
            amount = resp['data']['amount']
            Transaction.objects.filter(paystack_payment_reference=reference).update(status=status,
                                                                                        amount=amount)
            return Response(resp)
        return Response(resp)


class RefundViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for users to track their refund requests"""
    queryset = Refund.objects.all()
    serializer_class = serializers.RefundSerializer
    permission_classes = [AllowAny]

    # To process paystack refund
@action(detail=True, methods=["post"], url_path="process-refund")
def process_refund(self, request, pk=None):
    """Admin approves or denies a refund request"""
    refund = Refund.objects.get(ticket__id=pk)
    action = request.data.get("action")

    if action == "approve":
        if refund.process_paystack_refund():
            return Response({"message": "Refund approved and processed via Paystack"}, status=status.HTTP_200_OK)
        return Response({"error": "Paystack refund failed"}, status=status.HTTP_400_BAD_REQUEST)

    elif action == "deny":
        refund.status = "denied"
        refund.processed_at = now()
        refund.save()
        return Response({"message": "Refund denied"}, status=status.HTTP_200_OK)

    return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

# Paystack Webhook
@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack refund webhook events"""
    try:
        payload = json.loads(request.body)
        event = payload.get("event")

        if event == "refund.successful":
            paystack_reference = payload["data"]["transaction_reference"]

            # Find matching refund request
            try:
                ticket = Ticket.objects.get(ticket_code=paystack_reference)
                refund = Refund.objects.get(ticket=ticket, status="pending")
                
                # Mark refund as processed
                refund.status = "approved"
                refund.processed_at = now()
                refund.ticket.status = "available"
                refund.ticket.save()
                refund.save()

                return JsonResponse({"message": "Refund processed successfully"}, status=200)
            except (Ticket.DoesNotExist, Refund.DoesNotExist):
                return JsonResponse({"error": "No matching refund request found"}, status=404)

        return JsonResponse({"message": "Event ignored"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
