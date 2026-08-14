from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'


    def ready(self):
        # 手動 import，觸發 @receiver 註冊，這是關鍵！
        import accounts.models