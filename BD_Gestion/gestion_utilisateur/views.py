
from email.message import EmailMessage
from django.shortcuts import redirect, render,get_object_or_404


from.models import *
from gestion_content.models import *
from django.contrib import messages
import secrets
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse



def Home(request):
   actualite = BlogPost.objects.filter(valid=True).all()
   user_authenticate = request.user.is_authenticated
   usere = request.user
   
   if request.method == 'POST':
        user = request.user
        titre = request.POST.get('titre')
        contenue = request.POST.get('contenue')
        image = request.FILES.get('image')
        new = BlogPost.objects.create(
            title = titre,
            content = contenue,
            author = user,
            media = image,
            valid = False
        )
        new.save()
   today = timezone.localdate()  # Date du jour
   start_week = today - timedelta(days=today.weekday())  # Début de la semaine
   end_week = start_week + timedelta(days=6)  # Fin de la semaine
   start_next_week = end_week + timedelta(days=1)  # Début de la semaine prochaine
   end_next_week = start_next_week + timedelta(days=6)  # Fin de la semaine prochaine
   start_month = today.replace(day=1)  # Début du mois
   start_next_month = (start_month + timedelta(days=32)).replace(day=1)  # Début du mois prochain
   end_next_month = (start_next_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # Fin du mois suivant

   filter_type = request.GET.get("filter", "this_week")

   if filter_type == "this_week":
        events = Evenement.objects.filter(date_evenement__range=[start_week, end_week])
   elif filter_type == "next_week":
        events = Evenement.objects.filter(date_evenement__range=[start_next_week, end_next_week])
   elif filter_type == "this_month":
        events = Evenement.objects.filter(date_evenement__range=[start_month, start_next_month - timedelta(days=1)])
   elif filter_type == "next_month":
        events = Evenement.objects.filter(date_evenement__range=[start_next_month, end_next_month])
   else:
        events = Evenement.objects.all()
   return render(request,'gestion_utilisateur/index.html',{'actualite':actualite,'user_authenticate':user_authenticate,'events':events})


def Evenements(request):
   user_authenticate = request.user.is_authenticated
   evenements = Evenement.objects.all()
  

   today = timezone.localdate()  # Date du jour
   start_week = today - timedelta(days=today.weekday())  # Début de la semaine
   end_week = start_week + timedelta(days=6)  # Fin de la semaine
   start_next_week = end_week + timedelta(days=1)  # Début de la semaine prochaine
   end_next_week = start_next_week + timedelta(days=6)  # Fin de la semaine prochaine
   start_month = today.replace(day=1)  # Début du mois
   start_next_month = (start_month + timedelta(days=32)).replace(day=1)  # Début du mois prochain
   end_next_month = (start_next_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # Fin du mois suivant
   start_year = today.replace(month=1, day=1)  # Début de l'année en cours
   end_year = today.replace(month=12, day=31) 

   filter_type = request.GET.get("filter", "tous")

   if filter_type == "this_week":
        events = Evenement.objects.filter(date_evenement__range=[start_week, end_week])
   if filter_type == "tous":
        events = Evenement.objects.all()
   elif filter_type == "next_week":
        events = Evenement.objects.filter(date_evenement__range=[start_next_week, end_next_week])
   elif filter_type == "this_year":  # Ajout du filtre par année
        events = Evenement.objects.filter(date_evenement__range=[start_year, end_year])
   elif filter_type == "this_month":
        events = Evenement.objects.filter(date_evenement__range=[start_month, start_next_month - timedelta(days=1)])
   elif filter_type == "next_month":
        events = Evenement.objects.filter(date_evenement__range=[start_next_month, end_next_month])
   
       
   if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        events_data = list(events.values('id', 'title', 'date', 'description'))
        return JsonResponse({"events": events_data})

   return render(request, "gestion_utilisateur/evenement.html", {"events": events, "filter_type": filter_type,'user_authenticate':user_authenticate})

def signup(request):
    erreur = ""
    genrese = Genre.objects.all()
    annee_experience = Utilisateur.Annee_Experience
    pays = Utilisateur.PAYS_AFRICAINS
    role = Utilisateur.Role_choice
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        # firstname = request.POST.get('firsname')
        lastname = request.POST.get('lastname')
        password = request.POST.get('password')
        # password_confirme = request.POST.get('password_confirme')
        bio = request.POST.get('bio')
        profil = request.FILES.get('profil')
        # role = request.POST.get('role')
        annee_experience = request.POST.get('annee_experience')
        pays = request.POST.get('pays')
        # genre = request.POST.getlist('genre')
        user_exist = Utilisateur.objects.filter(username=username)
        if user_exist:
            erreur = "ce nom d'utilisateur existe deja veuillez essayer autre"
            return render(request,'gestion_utilisateur/signup.html')
        email_exist = Utilisateur.objects.filter(email=email)
        if email_exist:
            erreur = "ce nom d'utilisateur existe deja veuillez essayer autre"
            return render(request,'gestion_utilisateur/signup.html')
        # if password != password_confirme:
        #     erreur = "vos mot de passe ne sont pas identique"
        #     return render(request,'gestion_utilisateur/signup.html')
        token = secrets.token_urlsafe(32)
        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=password,
            # first_name=firstname,
            last_name=lastname,
            bio = bio,
            profil_picture = profil,
            # password_confirme=password_confirme,
            token = token,
            
            annee_experience = annee_experience,
            pays = pays,
            
            # genres = genre
        )
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)  # 🔥 Connexion correcte avec l'utilisateur authentifié
            return redirect('home')
    return render(request,'gestion_utilisateur/signup.html',{'genres':genrese,
                        "annee_experience": annee_experience,"role":role,'pays':pays})


# def auteur(request):

#     return render(request,'gestion_utilisateur/auteur.html')




def signin(request):
    errors=''
    
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            
            return redirect('home')
        else:
            errors="email ou mot de passe incorecte"
            return render(request,'gestion_utilisateur/connexion.html',{'errors':errors})
    return render(request,'gestion_utilisateur/connexion.html',{'errors':errors})

@login_required
def deconnexion(request):
    logout(request)
    return redirect('home')

# def signup(request):
#     error=''
#     formate='### ## ## ##'
#     email_exist=""
#     if request.method =='POST':
#         username=request.POST.get('username')
#         nom=request.POST.get('lastname')
#         prenom=request.POST.get('firtname')
#         email=request.POST.get('email')
#         phone=request.POST.get('phone')
#         image=request.FILES.get('image')
#         password=request.POST.get('password')
#         password2=request.POST.get('password2')
#         user_name=Utilisateur.objects.filter(username=username)
#         if user_name:
#             #  choix=f"{username}{random.randint(1,999)}"
#              errors=f"Cet identifiant existe deja voici une option pour vous {username}{random.randint(1,999)} "
#              return render(request,'Compte/signup.html',{'errors':errors})
#         email_exist=Utilisateur.objects.filter(email=email)
#         if email_exist:
#             errors=f"un utilisateur avec l'email {email} existe deja"
#             return render(request,'Compte/signup.html',{'errors':errors})
#         if password != password2:
#             errors="vos mots de passes ne sont pas conformes"
#             return render(request,'Compte/signup.html',{'errors':errors})
#         if len(password)<4:
#             errors="le mot de passe doit contenir au moins huit caractères"
#             return render(request,'Compte/signup.html',{'errors':errors})
#         if len(phone) <9 or len(phone) >9:
#             errors =f"mauvais format de telephone le numero {phone} de telephone doit être au format guinneen"
#             formate="premier"
#             print(phone)
#             return render(request,'Compte/signup.html',{'errors':errors,'formate':formate})
#         if phone[1] !=str(6) and phone[1] != str(2):
#             errors =f"mauvais format de telephone le numero de telephone doit être au format guinneen"
#             formate="deuxieme"
#             return render(request,'Compte/signup.html',{'errors':errors,'formate':formate})
#         token = secrets.token_urlsafe(32)
#         user=Utilisateur.objects.create_user(
#             username=username,
#             email=email,
#             password=password,
#             image=image,
#             first_name=prenom,
#             last_name=nom,
#             phone=str(phone),
#             password2=password2,
#             token = token
#         )
#         # user.save()
#         login(request,user)
#         return redirect('connexion')
#         # return render(request,'account/connexion.html')
#     return render(request,'Compte/signup.html')





def signin_auteur(request):
    user=request.user
    annee_experience = Utilisateur.Annee_Experience
    pays = Utilisateur.PAYS_AFRICAINS
    if request.method =='POST':
   
       
        bio = request.POST.get('bio')
        # profil = request.FILES.get('profil')
        role = request.POST.get('role')
        annee_experience = request.POST.get('annee_experience')
        pays = request.POST.get('pays')
        # image=request.FILES.get('image')
       
            
        
        user.bio = bio
        user.role = "auteur"
        user.annee_experience = annee_experience
        user.pays = pays
        user.save()
        return redirect('home')
        
    return render(request,'gestion_utilisateur/inscription_auteur.html',{"user":user,
                                "annee_experience": annee_experience,'pays':pays})

# def change_password(request):
#     errors=''
#     user=request.user
    
#     if request.method =='POST':
#         ancien_password=request.POST.get('password')
#         nouveau_password=request.POST.get('nouveau')
#         confirme_password=request.POST.get('confirme')
        
            
            
#         if not user.check_password(ancien_password):
        
#             messages.error(request,'le mot de passe entrer est erroné')
#             errors='le mot de passe entrez est erroné'
#             return render(request,'Compte/change_mot_de_pass.html',{'errors':errors})
#         if nouveau_password !=confirme_password:
            
#             messages.error(request,'vot mot de passe ne sont pas conforme')
#             errors='vos mot de passe ne sont pas conforme'
#             return render(request,'Compte/change_mot_de_pass.html',{'errors':errors})
#         user.set_password(nouveau_password)
#         user.save()
#         login(request,user)
#         return redirect('home')

#     return render(request,'Compte/change_mot_de_pass.html')

# def reset_password(request):
#     info =''
#     errors = ''
#     context = {}
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         user = Utilisateur.objects.filter(email=email)
#         if user:
#             token = user[0].token
#             suject = "recuperation de mot de passe"
#             message = f"coucou{user[0].username} ne vous enfaite pas vous n'avez qu'a cliquer sur ce lien pour obtenir un nouveau mot de passe http://localhost:8000/Compte/password/{token}"
#             from_email = settings.EMAIL_HOST_USER
#             to_email = email
#             email = EmailMessage(suject,message,from_email,[to_email])
#             email.send()
#             info ="un lien vient d'être envoyer sur votre boite mail merci de cliquer sur le lient afin de proceder à la recuperation du mot de passe"
#             context={
#                 'errors':errors,
#                 'info':info
#             }
#             return render(request,'Compte/reset_password.html',context)
#         else:
#             errors =f"desole l'utilisateur avec l'email {email} n'existe pas entrez votre vrai email"
#             context={
#                 'errors':errors,
#                 'info':info
#             }
#             return render(request,'Compte/reset_password.html',context)
#     return render(request,'Compte/reset_password.html',context)

# def modifier_password(request,token):
#     info = ''
#     errors = ''
#     if request.method == 'POST':
#         password = request.POST.get('password')
#         password2 = request.POST.get('password2')
#         if len(password)<4:
#             errors = "le mot de passe doit contenir au moins  cinq caractères"
#             return render(request,'Compte/password.html',{'errors':errors})
#         if password != password2:
#             errors = "vos mot de passe sont differents"
#             return render(request,'Compte/password.html',{'errors':errors})
#         user = Utilisateur.objects.filter(token=token)
#         users = user[0]
#         users.set_password(password)
#         users.save()
#         info = "felicitation votre mot de passe à été modifier avec succès connectez vous donc"
#         return redirect('connexion')
#     return render(request,'Compte/password.html')


# def filter_events(request):
#     today = timezone.localdate()  # Date du jour
#     start_week = today - timedelta(days=today.weekday())  # Début de la semaine
#     end_week = start_week + timedelta(days=6)  # Fin de la semaine
#     start_next_week = end_week + timedelta(days=1)  # Début de la semaine prochaine
#     end_next_week = start_next_week + timedelta(days=6)  # Fin de la semaine prochaine
#     start_month = today.replace(day=1)  # Début du mois
#     start_next_month = (start_month + timedelta(days=32)).replace(day=1)  # Début du mois prochain
#     end_next_month = (start_next_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # Fin du mois suivant

#     filter_type = request.GET.get("filter", "this_week")

#     if filter_type == "this_week":
#         events = Evenement.objects.filter(date__range=[start_week, end_week])
#     elif filter_type == "next_week":
#         events = Evenement.objects.filter(date__range=[start_next_week, end_next_week])
#     elif filter_type == "this_month":
#         events = Evenement.objects.filter(date__range=[start_month, start_next_month - timedelta(days=1)])
#     elif filter_type == "next_month":
#         events = Evenement.objects.filter(date__range=[start_next_month, end_next_month])
#     else:
#         events = Evenement.objects.all()  # Tous les événements par défaut

#     return render(request, "events.html", {"events": events, "filter_type": filter_type})

def detail_evenement(request,my_id):
    detail_event = get_object_or_404(Evenement,id=my_id)
    events = Evenement.objects.all()[:8]
    context = {
        'detail_event':detail_event,
        'events':events
    }
    return render(request,'gestion_utilisateur/detail_evenement.html',context)
    