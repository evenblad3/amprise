import bpy, bge, math
import wave
from array import array
from mathutils import Vector

# Code by BluePrintRandom.
# Save packed sound to disk, so we can load with wave
# (BGE api doesn't provide access to the raw data - as far as I know):
bpy.ops.file.unpack_all(method="USE_ORIGINAL")

# Even worse, there seems to be no way to get the wav name from the
# actuator, so we have to hardcode:
WAV_NAME = ("C:\\Users\\Jeba\\Documents\\BGE\\range\\ratm_killing_in_the_name.wav")

# Actual work:
def amplitude(wav, t):
    head = int(t * wav.getframerate())
    delta = head - wav.tell()
    
    if delta < 0:
        delta = head - 0
        wav.rewind()
        
    chunk = array('h', wav.readframes(delta))
    lc = len(chunk)
    return (abs(sum(chunk) / lc)) if lc else 0 

def amp_z(cont):
    own = cont.owner
    act_snd = cont.actuators["Sound"]
    
    if not "init" in own:
        own["init"] = True
        own["wav"] = wave.open(WAV_NAME)
        own['x']=0
        cont.activate(act_snd)
    round = 8
    own['x'] = ((own['x'] * (round-1)) + (amplitude(own["wav"], act_snd.time) / 100))/round
    for obj in own.scene.objects: # Gets every object data in the scene
        if 'init2' not in obj:
            obj['init2']=obj.worldPosition.copy()
        val = math.sin((obj.worldPosition.magnitude*2)+(own['x']*0.66))
        # Just to debug
        own["getVal"] = val
        own["getVal2"] = val*-1 # getVal2 prop convert the negative value to positive so the lights react to the audio properly
        
        #val = math.sin(obj.worldPosition[0])+math.sin(obj.worldPosition[1])+(own['x']*3.28) * .66
        #-----------------------------------------   # This part was needed to solve an error.
        if type(obj) == bge.types.KX_GameObject:     # If the data is a GameObject,
            obj.color = [val,val,val,1]              # Change the color including the alpha
            obj.worldPosition = obj['init2']+Vector([0,0,val]) #Change the objects' position according the the music
        elif type(obj) == bge.types.KX_LightObject:  # If the data we got is a LightObject,
            obj.color = [own["getVal2"],own["getVal2"],own["getVal2"]] # Change its color only (cuz it has no alpha (thanks BPR))
        elif type(obj) == bge.types.KX_FontObject:
            obj.text = str(val)[:4]                  #Display the math value of "val" and subscript it (it shows a long number)
            obj.worldPosition = [0,0,val/4+3]        # Let the FontObject react to audio but not as much as every object do.
        #------------------------------------------
        
