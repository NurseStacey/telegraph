from django.shortcuts import render, redirect


def create_message(request):
    return render(request,'message/create_message.html',{})
