class DBRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'sde':
            return 'sde'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'sde':
            return 'sde'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'sde' and \
           obj2._meta.app_label == 'sde':
           return True
        elif obj1._meta.app_label == 'sde' or \
           obj2._meta.app_label == 'sde':
           return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'sde':
            return app_label == 'sde'
        elif app_label == 'sde':
            return False
        return None