"""
Code to be executed only once at startup.
It is a hook defined in varapp/__init__.py .
"""
from django.apps import AppConfig
from django.conf import settings
import sys, logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(message)s')


class VarappConfig(AppConfig):
    """`this.ready()` gets executed when the app is fully loaded (models etc.)
    It is called in varapp/__init__.py, and once per Apache process.
    """
    name = 'varapp'
    verbose_name = "Varapp"
    def ready(self):
        from varapp.common import manage_dbs, utils
        from varapp.common.versioning import add_versions_all

        # Check that there are tables in the users_db,
        # because this code is also run when manage.py is used,
        # for instance to generate the tables.
        user_db_ready = len(utils.table_names('default')) != 0

        # At startup, fill settings.DATABASES with what is in VariantsDb.
        # Do not add any new db here, as unlike deactivation, inserts
        # are not idempotent and this code could be executed several times.
        if user_db_ready:
            manage_dbs.copy_VariantsDb_to_settings()

            if settings.WARMUP_STATS_CACHE:
                self.warmup_stats()

            if settings.WARMUP_GENOTYPES_CACHE:
                self.warmup_genotypes()

            # Update the *annotation* table with versions of all programs used,
            # i.e. Gemini, VEP, their dbs, etc.
            add_versions_all()

    @staticmethod
    def warmup_stats():
        """Generate the stats cache for all active dbs"""
        from varapp.models.users import VariantsDb
        from varapp.stats.stats_service import stats_service
        for db in VariantsDb.objects.filter(is_active=1):
            stats_service(db.name)

    @staticmethod
    def warmup_genotypes():
        """Generate the genotypes cache for all active dbs"""
        from varapp.models.users import VariantsDb
        from varapp.variants.genotypes_service import genotypes_service
        for db in VariantsDb.objects.filter(is_active=1):
            genotypes_service(db.name)

    #@staticmethod
    #def warmup_annotation():
    #    from varapp.models.users import VariantsDb
    #    from varapp.annotation.annotation_service import gene_detailed_service, gene_summary_service
    #    for db in VariantsDb.objects.filter(is_active=1, name__in=['test','lgueneau']):
    #        gene_detailed_service(db.name)
    #        gene_summary_service(db.name)


