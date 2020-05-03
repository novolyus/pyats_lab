# Metaparser
from genie.metaparser import MetaParser
from genie import parsergen
from genie.metaparser.util.schemaengine import Any, Optional

# parser utils
from genie.libs.parser.utils.common import Common

from pprint import pprint
from genie.conf import Genie

from genie.ops.base import Base

# =============================================
# Parser for ASA 'show counters'
# =============================================


class ShowCountersSchema(MetaParser):
    """Schema for show counters
    """

    schema = {
        Any():{
            Any():{
                'Protocol': str,
                'Counter': str,
                'Value': str,
                'Context': str,
                },
           },
        }


class ShowCounters(ShowCountersSchema):
# class ShowCounters():
    """ Parser for show counters """

    def cli(self):
        # excute command to get output
        cmd = 'show counters'
        output = self.device.execute(cmd)

        header = ['Protocol', 'Counter', 'Value', 'Context']

        result = parsergen.oper_fill_tabular(device_output=output, device_os='asa', header_fields=header, index=[1, 0])
        pprint(result.entries)
        return result.entries


#Create  Class HealthASA (Genie Ops)
class HealthASA(Base):

    def learn(self, custom=None):

        # Capture output from show counters parser
        src = '[(?P<counter_name>.*)][(?P<protocol_name>.*)]'
        dest = 'info[(?P<counter_name>.*)][(?P<protocol_name>.*)]'
        req_keys = ['Value']
        for key in req_keys:
            self.add_leaf(cmd=ShowCounters,
                          src=src + f'[{key}]',
                          dest=dest + f'[{key}]')

        #Add ops data to the HealthASA ojbect
        self.make()


if __name__ == '__main__':
    testbed = Genie.init('pyats_testbed.yaml')
    asa = testbed.devices['asav-1']
    asa.connect()
        
    myasahealth = HealthASA(device=asa)
    myasahealth.learn()
    pprint(myasahealth.info)
                
