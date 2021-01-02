from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
            
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    NOOB = "Noob"
    INTERMEDIATE = "Intermediate"
    PROFESSIONAL = "Professional"
    MASTER = "Master"
    JEDI = "Jedi"
    LEVELS = [
    (NOOB, 'NOOB'),
    (INTERMEDIATE, 'INTERMEDIATE'),
    (PROFESSIONAL, 'PROFESSIONAL'),
    (MASTER, 'MASTER'),
    (JEDI, 'JEDI'),
    ]
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'),max_length=61)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    imageUrl = models.URLField(blank=True,null=True)
    friends = models.ManyToManyField("self",blank=True)
    isUsernameSet = models.BooleanField(default=False)
    level = models.CharField(choices=LEVELS, max_length=15,default=NOOB)
    points = models.IntegerField(default=0)
    usernameUpdated = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Deselect this instead of deleting accounts.'
        ),
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

class GameRoom(models.Model):
    room_name = models.CharField(max_length=100)
    is_friend = models.BooleanField(default=False)
    is_full = models.BooleanField(default=False)

    def __str__(self):
        return self.room_name


class Game_Model(models.Model):
    room = models.ForeignKey(GameRoom, default="",related_name='game_model',on_delete=models.CASCADE)
    player1 = models.ForeignKey(User,on_delete=models.CASCADE,related_name='player_1',blank=True)
    player2 = models.ForeignKey(User,on_delete=models.CASCADE,related_name='player_2',blank=True)
    first_player = models.CharField(max_length=50,blank=True,default="")
    movements = ArrayField(models.IntegerField(),blank=True,default=list)
    winner = models.CharField(max_length=1,blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True,blank=True)
    
    def __str__(self):
        return '%s  on %s' %(self.player1.username,format(self.timestamp))

    def __unicode__(self):
        return '[{timestamp}] {handle}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return format(self.timestamp)

class ChatGroup(models.Model):
    groupName = models.CharField(max_length=150)
    creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="creator")
    members = models.ManyToManyField(User,related_name="members")

    def __str__(self):
        return self.groupName

class SocialLogin(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    email = models.EmailField(_('email address'), unique=True)
    userID = models.CharField(max_length=50,blank=True,default="")
    socialmedia = models.CharField(_("social media"), max_length=10)
    accessToken = models.CharField(_("access token"), max_length=4096)

    def __str__(self):
        return self.user.username

class Imag(models.Model):
    user = models.ForeignKey(User, verbose_name=_("userimage"), default=None, on_delete=models.CASCADE)
    file = models.ImageField(_("image"), upload_to="images/", height_field=None, width_field=None, max_length=None)
    
    def __str__(self):
        return self.user.username