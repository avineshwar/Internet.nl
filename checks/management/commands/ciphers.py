from django.core.management.base import BaseCommand, CommandError
from checks.tasks.cipher_info import load_cipher_info, CipherScoreAndSecLevel


class Command(BaseCommand):
    help = (
        'List the supported SSL/TLS ciphers, ala the openssl ciphers command. '
        'Tip; Pipe the output through the `column -t` command.')

    def add_arguments(self, parser):
        parser.add_argument(
            'ciphers', nargs='*',
            help='Zero or more OpenSSL cipher names to show details for.')

    def handle(self, *args, **options):
        cipher_infos = load_cipher_info()
        v_level = options['verbosity']

        for ci in cipher_infos.values():
            if options['ciphers'] and ci.name not in options['ciphers']:
                continue

            cipher_string = f'{ci.name}'

            if v_level > 0:
                cipher_string += (
                    f'\t{ci.tls_version}'
                    f'\tKx={ci.kex_algs}'
                    f'\tAu={ci.auth_alg}'
                    f'\tEnc={ci.bulk_enc_alg}({ci.bulk_enc_alg_sec_len})'
                    f'\tMac={ci.mac_alg}'
                )

            if v_level > 1:
                cipher_string += f'\tConn={ci.conn_class.__name__}'

            if v_level > 2:
                sec_level = CipherScoreAndSecLevel.determine_appendix_c_sec_level(ci).name
                formatted_score = CipherScoreAndSecLevel.format_score(
                    CipherScoreAndSecLevel.calc_cipher_score(ci))
                cipher_string += f'\tSecLevel={sec_level}'
                cipher_string += f'\tScore={formatted_score}'

            self.stdout.write(cipher_string)
