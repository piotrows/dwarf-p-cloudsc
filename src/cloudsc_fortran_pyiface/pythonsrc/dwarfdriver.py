import sys 
sys.path.append('../../build/src/cloudsc_fortran_pyiface')
sys.path.append('../../build/lib')
sys.path.append('.')
from pathlib import Path
import numpy as np
from collections import OrderedDict
import cloudsc as clsc
from cloudsc_data import define_fortran_fields,load_input_parameters,load_input_fortran_fields,cloudsc_validate,convert_fortran_output_to_python,load_reference_fields
from operator import itemgetter

 
nproma=100
numomp=1
nlev=137
ngptot=100
ngptotg=100
nblocks=1
ndim=5
ptsphy=3600.

clsfields=define_fortran_fields(nproma,nlev,nblocks)

for fieldname in clsfields.keys():
     locals()[fieldname]=itemgetter(fieldname)(clsfields)



rootpath = Path(__file__).resolve().parents[3]
input_path = rootpath/'config-files/input.h5'


# Get referennce solution fields from file
ref_path = rootpath/'config-files/reference.h5'
ref_fields = load_reference_fields(path=ref_path)


NCLV = 5      # number of microphysics variables
NCLDQL = 1    # liquid cloud water
NCLDQI = 2    # ice cloud water
NCLDQR = 3    # rain water
NCLDQS = 4    # snow
NCLDQV = 5    # vapour

ydecldp, ydomcst, ydoethf, ydephli = load_input_parameters(input_path,ydecldp,ydephli,ydomcst,ydoethf)

input_fort_fields = load_input_fortran_fields(input_path,nproma,nlev,nblocks,clsfields)

for fieldname in input_fort_fields.keys():
     locals()[fieldname]=input_fort_fields[fieldname]


clsc.cloudsc_driver_pyiface_mod.cloudsc_driver_no_derv_tpes(
                         numomp, nproma, nlev, ngptot, ngptotg,
                         NCLDQV, NCLDQL, NCLDQR, NCLDQI, NCLDQS, NCLV,
                         kfldx, ptsphy,
                         pt, pq,
                         buffer_tmp, buffer_loc,
                         pvfa, pvfl, pvfi, pdyna, pdynl, pdyni,
                         phrsw, phrlw, 
                         pvervel, pap, paph,
                         plsm, ldcum, ktype,
                         plu, plude, psnde, pmfu, pmfd,
                         pa, pclv, psupsat,
                         plcrit_aer, picrit_aer, pre_ice, 
                         pccn, pnice,
                         pcovptot, prainfrac_toprfz,
                         pfsqlf,   pfsqif ,  pfcqnng,  pfcqlng, 
                         pfsqrf,   pfsqsf ,  pfcqrng,  pfcqsng, 
                         pfsqltur, pfsqitur,  
                         pfplsl, pfplsn, pfhpsl, pfhpsn,
                         ydomcst, ydoethf, ydecldp, ydephli)

output_fields = convert_fortran_output_to_python (nproma,nlev,nblocks,input_fort_fields)
#                                                 plude, pcovptot,
#                                                 pfplsl, pfplsn, pfhpsl, pfhpsn, 
#                                                 pfsqlf,   pfsqif ,  pfcqnng,  pfcqlng,
#                                                 pfsqrf,   pfsqsf ,  pfcqrng,  pfcqsng,
#                                                 pfsqltur, pfsqitur,
#                                                 prainfrac_toprfz,
#                                                 buffer_loc )

print ("Python-side validation:")
cloudsc_validate(output_fields, ref_fields)
