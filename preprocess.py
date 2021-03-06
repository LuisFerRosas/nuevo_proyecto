

from torch.utils.data import Dataset
import numpy as np

import collections

import torch as t

from nuevoPreproseced import sequence_partitura,cargarVocabulario
from procesing_audio import cargarArchivosNPY,cargarArchivosNPY_sinCorte


    

class DatasetNuevo(Dataset):
    
    def __init__(self,  pathPartituras,pathVocabulario,pathArchivoNPY,pathcomple):
        self.pathPartituras=pathPartituras
        self.vocabPartitura =cargarVocabulario(pathVocabulario=pathVocabulario)
        self.waveform,self.nombresAudio=cargarArchivosNPY(pathArchivoNPY)
        self.waveComple,self.nomComple=cargarArchivosNPY_sinCorte(pathcomple)

    def __len__(self):
        return len(self.nombresAudio)

    def __getitem__(self, idx):
        wave_nameComple=self.nomComple[idx]
        wav_name = self.nombresAudio[idx]
        partitura_tokenizada = np.asarray(sequence_partitura(self.pathPartituras+'/'+wav_name[:-3]+'xml',self.vocabPartitura), dtype=np.int32)
        wave_mfcc=self.waveform[idx]
        partitura_length=len(partitura_tokenizada)
        wave_mfcc_Comple=self.waveComple[wave_nameComple]
        salida={'partitura_tokenizada':partitura_tokenizada,'wave_mfcc':wave_mfcc,'partitura_length':partitura_length,'wave_Comple':wave_mfcc_Comple}
        return salida
    
    
def obtenerDatos(pathPartituras,pathVocabulario,pathArchivoNPY,pathcomple):
    return DatasetNuevo(pathPartituras=pathPartituras,pathVocabulario=pathVocabulario,pathArchivoNPY=pathArchivoNPY,pathcomple=pathcomple)




def collate_fn_nuevo(batch):
    if isinstance(batch[0], collections.Mapping):
        partitura = [d['partitura_tokenizada'] for d in batch]
        mfcc = [d['wave_mfcc'] for d in batch]
        mfcc2 = [d['wave_Comple'] for d in batch]
        partitura_length = [d['partitura_length'] for d in batch]
        partitura = [i for i,_ in sorted(zip(partitura, partitura_length), key=lambda x: x[1], reverse=True)]
        partitura = _prepare_data(partitura).astype(np.int32)
        
        return t.LongTensor(partitura),t.Tensor(mfcc).float(),t.LongTensor(partitura_length),t.Tensor(mfcc2).float()


def _pad_data(x, length):
    _pad = 0
    return np.pad(x, (0, length - x.shape[0]), mode='constant', constant_values=_pad)

def _prepare_data(inputs):
    max_len = max((len(x) for x in inputs))
    return np.stack([_pad_data(x, max_len) for x in inputs])

def get_param_size(model):
    params = 0
    for p in model.parameters():
        tmp = 1
        for x in p.size():
            tmp *= x
        params += tmp
    return params







