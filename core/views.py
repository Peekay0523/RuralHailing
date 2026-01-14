from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rides.models import Ride
from core.models import Payment
from core.serializers import PaymentSerializer
import uuid

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@api_view(['GET'])
def api_status(request):
    return Response({'status': 'API is running'})

# Set up Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ride_id = request.data.get('ride_id')
        payment_method = request.data.get('payment_method', 'card')

        try:
            ride = Ride.objects.get(id=ride_id, passenger=request.user)
        except Ride.DoesNotExist:
            return Response(
                {'error': 'Ride not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if ride.payment_status != 'pending':
            return Response(
                {'error': 'Payment already processed for this ride'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create a PaymentIntent with Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(ride.fare * 100),  # Amount in cents
                currency='usd',
                metadata={
                    'ride_id': ride.id,
                    'user_id': request.user.id
                }
            )

            # Create payment record
            payment = Payment.objects.create(
                ride=ride,
                amount=ride.fare,
                payment_method=payment_method,
                transaction_id=intent.id,
                status='pending'
            )

            return Response({
                'client_secret': intent.client_secret,
                'payment_id': payment.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ProcessPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')

        try:
            # Retrieve the PaymentIntent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # Find the corresponding payment
            try:
                payment = Payment.objects.get(transaction_id=payment_intent_id)
            except Payment.DoesNotExist:
                return Response(
                    {'error': 'Payment record not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Update payment status based on Stripe
            if intent.status == 'succeeded':
                payment.status = 'completed'
                payment.ride.payment_status = 'completed'
                payment.ride.save()
            elif intent.status == 'requires_payment_method':
                payment.status = 'failed'
            else:
                payment.status = intent.status

            payment.save()

            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class CashPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ride_id = request.data.get('ride_id')

        try:
            ride = Ride.objects.get(id=ride_id, passenger=request.user)
        except Ride.DoesNotExist:
            return Response(
                {'error': 'Ride not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if ride.payment_status != 'pending':
            return Response(
                {'error': 'Payment already processed for this ride'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create cash payment record
        payment = Payment.objects.create(
            ride=ride,
            amount=ride.fare,
            payment_method='cash',
            transaction_id=f"cash_{uuid.uuid4()}",
            status='completed'
        )

        # Update ride payment status
        ride.payment_status = 'completed'
        ride.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)