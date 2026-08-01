import matplotlib as mpl


from capstone.visualization.visuals import PLT_PARAMS

ORDER = ["Not Contacted", "Contacted"]
LABEL = {"Not Contacted": "Not Contacted", "Contacted": "Contacted"}

mpl.rcParams.update(PLT_PARAMS)  # type: ignore
