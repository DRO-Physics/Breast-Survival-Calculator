import PySimpleGUI as sg
from Survival_Calculator import Survival_Calculator
import matplotlib.pyplot as plt

sg.theme('Reddit')

def draw_plot(results):
    # plt.plot([0.1, 0.2, 0.5, 0.7])
    plt.plot(results['time'], results['s_mean'], 'r-', label='DeepSurv')
    plt.fill_between(results['time'], results['s_mean']-results['s_std'],  results['s_mean']+results['s_std'], alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.show(block=True)

## Defining layout of the GUI
## Defining top input layer
input_layer = [
    [
        sg.Text('Age At Diagnosis: '),
        sg.InputText(default_text= '40.0', size = (20,1), key='-AGE-', justification='left'),
        sg.Text('Grade: '),
        sg.Combo(['1', '2', '3'], size = (10,1), key='-GRADE-', default_value='1'),
    ],
    [
        sg.Text('T Stage: '),
        sg.Combo(['0', '1', '2', '3', '4'], size = (10,1), key='-T-', default_value='1'),
        sg.Text('N Stage: '),
        sg.Combo(['0', '1', '2', '3'], size = (10,1), key='-N-', default_value='1'),
        sg.Text('M Stage '),
        sg.Combo(['0', '1'], size = (10,1), key='-M-', default_value='1')
    ],
    [
        sg.Text('ER: '),
        sg.Combo(['Pos', 'Neg'], size = (10,1), key='-ER-', default_value='Pos'),
        sg.Text('PR: '),
        sg.Combo(['Pos', 'Neg'], size = (10,1), key='-PR-', default_value='Pos'),
        sg.Text('HER2: '),
        sg.Combo(['Pos', 'Neg'], size = (10,1), key='-HER2-', default_value='Pos')
    ],
    [
        sg.Text('Invasion: '),
        sg.Combo(['Yes', 'No'], size = (10,1), key='-INVADE-', default_value='Yes')
    ],
    [
        sg.Text('Size (mm): '),
        sg.InputText(default_text= '1', size = (10,1), key='-SIZE-', justification='left'),
        sg.Text('Nodes: '),
        sg.InputText(default_text= '1', size = (10,1), key='-NODES-', justification='left')
    ],
    [
        sg.Button("Survival Curve", enable_events=True, key='-CALCULATE-', bind_return_key=True),
        sg.Text('Powered by DRO  (3/2/21): ',font=('Helvetica', 8), justification='right')
    ],
    [sg.Text('_'  * 100, size=(65, 1))]
]

## Defining total layout
layout = [
    [sg.Column(input_layer)]
]

## Start the Window
window = sg.Window(title="Breast Survival Calculator", layout=layout)

while True:
    event, values = window.read()
    # End program if user closes window
    if event == sg.WIN_CLOSED:
        break

    ## Plot the survival curve
    if event == '-CALCULATE-':
        age = float(values['-AGE-'])
        grade = int(values['-GRADE-'])
        tstage= int(values['-T-'])
        nstage= int(values['-N-'])
        mstage= int(values['-M-'])
        er = (values['-ER-'] == 'Pos') * 1.0
        pr = (values['-PR-'] == 'Pos') * 1.0
        her2 = (values['-HER2-'] == 'Pos') * 1.0
        invade = (values['-INVADE-'] == 'Yes') * 1.0
        size = float(values['-SIZE-'])
        nodes = float(values['-NODES-'])

        results = Survival_Calculator(age, tstage, nstage, mstage, grade, er, pr, her2, invade, size, nodes).results

        draw_plot(results)


window.close()
