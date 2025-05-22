from rest_framework import serializers
from .models import ExpenseName, CashInFlowName, CashInFlow, Expense
from ..stores.models import Store
from ..stores.serializers import StoreSerializer


class ExpenseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseName
        fields = '__all__'


class CashInFlowNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashInFlowName

        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), write_only=True)
    expense_name = serializers.PrimaryKeyRelatedField(queryset=ExpenseName.objects.all(), write_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    history = serializers.JSONField(default=dict, read_only=True)

    store_read = StoreSerializer(read_only=True)
    expense_name_read = ExpenseNameSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = ["id", "store",
                  "expense_name",
                  "amount",
                  "user",
                  "history",
                  "store_read",
                  "expense_name_read",
                  'comment']

    def create(self, validated_data):
        # user = validated_data.pop('user')
        expense_name = validated_data.pop('expense_name')
        store = validated_data.pop('store')
        amount = validated_data.pop('amount')
        comment = validated_data.pop('comment')

        expense_store = Store.objects.get(pk=store.pk)
        if expense_store.budget < amount:
            raise serializers.ValidationError('Expense amount must be greater than budget')
        else:
            expense_store.budget -= amount
            expense_store.save()
        history = {
            # 'user': user,

            'expense_name': expense_name.name,
            'amount': float(amount),
            'comment': comment,

        }
        expense = Expense.objects.create(expense_name=expense_name,
                                         amount=amount, store=store,
                                         history=history, comment=comment, **validated_data)
        return expense

    def update(self, instance, validated_data):

        amount = validated_data.pop('amount')
        comment = validated_data.pop('comment')
        history = instance.history
        history[f'comment'] = f'{amount} - {comment}'
        expense_store = Store.objects.get(pk=instance.store.pk)


        if instance.amount > amount:

            difference = int(instance.amount) - int(amount)
            expense_store.budget += difference
            expense_store.save()
        elif amount > instance.amount:
            difference = int(amount) - int(instance.amount)
            expense_store.budget -= difference
            expense_store.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.amount = amount
        instance.save()

        return instance


class CashInFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashInFlow
