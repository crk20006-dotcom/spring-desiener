


def gear_module():
    page_header("⚙️ Gear & Machine Design","A focused workspace for external spur-gear pairs and ideal gear-train calculations.")
    with st.expander("Gear inputs",expanded=True):
        a,b,c=st.columns(3); z1=a.number_input("Driver teeth",8,300,20,key="g_z1"); z2=b.number_input("Driven teeth",8,600,60,key="g_z2"); rpm=a.number_input("Driver speed (rpm)",1.0,100000.0,1200.0,key="g_rpm")
        module=c.number_input("Module (mm)",0.25,50.0,2.0,key="g_mod"); power=b.number_input("Input power (kW)",0.01,10000.0,2.0,key="g_power"); eff=c.number_input("Estimated efficiency (%)",1.0,100.0,95.0,key="g_eff")
    ratio=z2/z1; out_rpm=rpm/ratio; out_power=power*eff/100; Tin=9550*power/rpm; Tout=9550*out_power/out_rpm
    d1=module*z1; d2=module*z2; center=(d1+d2)/2
    metric_row([("Gear ratio",f"{ratio:.3f}:1","Driven teeth / driver teeth"),("Output speed",f"{out_rpm:.1f} rpm","Ideal speed ratio"),("Output torque",f"{Tout:.2f} N·m","Includes assumed efficiency"),("Centre distance",f"{center:.2f} mm","Standard external spur gears")])
    st.caption(f"Driver pitch diameter: {d1:.2f} mm · Driven pitch diameter: {d2:.2f} mm · Input torque: {Tin:.2f} N·m")
    t=np.linspace(0,2*np.pi,160); f=go.Figure()
    f.add_trace(go.Scatter(x=d1/2*np.cos(t),y=d1/2*np.sin(t),mode="lines",name=f"Driver ({z1} teeth)"))
    f.add_trace(go.Scatter(x=center+d2/2*np.cos(t),y=d2/2*np.sin(t),mode="lines",name=f"Driven ({z2} teeth)"))
    f.update_layout(title="Pitch-circle layout (schematic)",xaxis_title="X (mm)",yaxis_title="Y (mm)",yaxis=dict(scaleanchor="x",scaleratio=1))
    st.plotly_chart(chart_layout(f,400),use_container_width=True)
    df=pd.DataFrame([{"driver_teeth":z1,"driven_teeth":z2,"gear_ratio":ratio,"input_speed_rpm":rpm,"output_speed_rpm":out_rpm,"input_power_kW":power,"assumed_efficiency_pct":eff,"output_power_kW":out_power,"input_torque_Nm":Tin,"output_torque_Nm":Tout,"module_mm":module,"driver_pitch_diameter_mm":d1,"driven_pitch_diameter_mm":d2,"centre_distance_mm":center}])
    downloads("gear_analysis",df,"Gear Pair Analysis Report",[f"Driver teeth: {z1}",f"Driven teeth: {z2}",f"Ratio: {ratio:.4f}:1",f"Input speed: {rpm:.2f} rpm",f"Output speed: {out_rpm:.2f} rpm",f"Input power: {power:.3f} kW",f"Assumed efficiency: {eff:.2f}%",f"Output torque: {Tout:.3f} N m",f"Centre distance: {center:.3f} mm","Schematic pitch circles only; tooth profile/contact ratio/bending and pitting strength are not analysed."])
    st.warning("Preliminary ideal gear-pair tool. Tooth strength, contact ratio, backlash, lubrication, bearing loads and applicable gear standards are not assessed.")

def thermal_module():
    page_header("🌡️ Thermal & Welding Heat Simulation","A simplified transient heat-source model for learning and visualization; not a welding procedure predictor.")
    a,b,c=st.columns(3); q=a.number_input("Heat input power (W)",10.0,100000.0,1200.0,key="th_q"); alpha=b.number_input("Thermal diffusivity (mm²/s)",0.01,200.0,12.0,key="th_a"); duration=c.number_input("Heating time (s)",1.0,3600.0,60.0,key="th_t")
    eta=st.slider("Effective heat fraction",0.1,1.0,0.75,0.05,key="th_eta"); xlim=st.slider("Field half-width (mm)",10,200,60,key="th_x")
    # Educational 2D Gaussian field; not a calibrated weld thermal model.
    xs=np.linspace(-xlim,xlim,81); ys=np.linspace(-xlim,xlim,81); X,Y=np.meshgrid(xs,ys); r2=X**2+Y**2
    spread=max(2.0,math.sqrt(4*alpha*duration)); amp=q*eta/(4*math.pi*max(alpha,0.01)*duration)
    temp=20+amp*np.exp(-r2/(spread**2))*duration/100
    peak=float(temp.max()); metric_row([("Peak illustrative temperature",f"{peak:.1f} °C","Model-dependent estimate"),("Diffusion length scale",f"{spread:.2f} mm","sqrt(4 α t)"),("Effective heat input",f"{q*eta:.1f} W","Power × heat fraction")])
    f=go.Figure(go.Contour(x=xs,y=ys,z=temp,colorscale="Inferno",colorbar=dict(title="°C"),contours=dict(showlabels=True)))
    f.update_layout(title="Illustrative 2D heat field",xaxis_title="Distance x (mm)",yaxis_title="Distance y (mm)")
    st.plotly_chart(chart_layout(f,470),use_container_width=True)
    times=np.linspace(1,duration,80); center_t=20+(q*eta/(4*math.pi*alpha*times))*times/100
    ft=go.Figure(go.Scatter(x=times,y=center_t,mode="lines",name="Center-point trend")); ft.update_layout(title="Simplified center-point trend",xaxis_title="Time (s)",yaxis_title="Illustrative temperature (°C)")
    st.plotly_chart(chart_layout(ft,330),use_container_width=True)
    df=pd.DataFrame({"x_mm":X.ravel(),"y_mm":Y.ravel(),"illustrative_temperature_C":temp.ravel()})
    downloads("thermal_simulation",df,"Thermal Simulation Report",[f"Input power: {q:.2f} W",f"Effective heat fraction: {eta:.3f}",f"Thermal diffusivity: {alpha:.4f} mm²/s",f"Heating time: {duration:.2f} s",f"Illustrative peak temperature: {peak:.3f} °C","The Gaussian field is a teaching visualization, not a validated weld heat-transfer model."])
    st.warning("This simplified Gaussian visualization is not calibrated to a real weld, boundary conditions, material properties or process. Do not use it to select welding parameters or certify safety.")

def robotics_module():
    page_header("🦾 Robotics & Kinematics","Two-link planar robot arm: solve endpoint position from joint angles and export the pose readings.")
    a,b,c=st.columns(3); L1=a.number_input("Link 1 length (mm)",10.0,2000.0,300.0,key="r_l1"); L2=b.number_input("Link 2 length (mm)",10.0,2000.0,220.0,key="r_l2"); t1=c.slider("Joint 1 angle (°)",-180,180,35,key="r_t1"); t2=st.slider("Joint 2 relative angle (°)",-180,180,55,key="r_t2")
    r1=math.radians(t1); r2=math.radians(t1+t2); x1=L1*math.cos(r1); y1=L1*math.sin(r1); x2=x1+L2*math.cos(r2); y2=y1+L2*math.sin(r2); reach=math.hypot(x2,y2)
    metric_row([("End-effector X",f"{x2:.2f} mm","Base origin at (0,0)"),("End-effector Y",f"{y2:.2f} mm","Planar vertical coordinate"),("Reach from base",f"{reach:.2f} mm","Euclidean endpoint distance")])
    f=go.Figure(); f.add_trace(go.Scatter(x=[0,x1,x2],y=[0,y1,y2],mode="lines+markers+text",text=["Base","Joint 1","Tool tip"],textposition="top center",line=dict(width=8),marker=dict(size=12),name="Robot arm")); f.add_shape(type="circle",x0=-(L1+L2),y0=-(L1+L2),x1=L1+L2,y1=L1+L2,line=dict(dash="dot",color="gray")); f.update_layout(title="Planar robot arm pose",xaxis_title="X (mm)",yaxis_title="Y (mm)",yaxis=dict(scaleanchor="x",scaleratio=1))
    st.plotly_chart(chart_layout(f,470),use_container_width=True)
    df=pd.DataFrame([{"link1_mm":L1,"link2_mm":L2,"joint1_deg":t1,"joint2_relative_deg":t2,"joint2_absolute_deg":t1+t2,"end_effector_x_mm":x2,"end_effector_y_mm":y2,"reach_mm":reach}])
    downloads("robot_kinematics",df,"Robot Kinematics Report",[f"Link 1: {L1:.3f} mm",f"Link 2: {L2:.3f} mm",f"Joint 1 angle: {t1} degrees",f"Joint 2 relative angle: {t2} degrees",f"End effector X: {x2:.3f} mm",f"End effector Y: {y2:.3f} mm",f"Reach: {reach:.3f} mm","Planar forward kinematics only; dynamics, collision and inverse-kinematics constraints are not included."])
    st.info("Uses planar forward kinematics. Joint limits, collision detection, dynamics and actuator sizing are not included.")

def materials_module():
    page_header("📈 Materials & Stress–Strain","Idealized tensile stress–strain curve with elastic modulus, yield point and post-yield response.")
    a,b,c=st.columns(3); E=a.number_input("Young's modulus (GPa)",1.0,500.0,200.0,key="m_E"); ys=b.number_input("Yield strength (MPa)",1.0,3000.0,250.0,key="m_yield"); uts=c.number_input("Ultimate strength (MPa)",1.0,5000.0,450.0,key="m_uts")
    elong=st.slider("Illustrative strain range (%)",0.2,30.0,5.0,0.2,key="m_strain")
    if uts<ys: st.warning("Ultimate strength is below yield strength. Adjust the inputs for a typical ductile-metal illustration.")
    strain=np.linspace(0,elong/100,250); e=E*1000; ey=ys/e; stress=np.where(strain<=ey,e*strain,ys+(uts-ys)*np.minimum((strain-ey)/max(strain.max()-ey,1e-9),1))
    sel=st.slider("Selected engineering strain (%)",0.0,float(elong),min(float(elong),1.0),0.1,key="m_selstrain")/100
    selected_stress=float(np.interp(sel,strain,stress)); metric_row([("Young's modulus",f"{E:.2f} GPa","Elastic slope"),("Yield strain estimate",f"{ey*100:.3f}%","Yield strength / modulus"),("Selected stress",f"{selected_stress:.2f} MPa",f"At {sel*100:.2f}% strain")])
    f=go.Figure(); f.add_trace(go.Scatter(x=strain*100,y=stress,mode="lines",name="Idealized material curve",line=dict(width=3))); f.add_trace(go.Scatter(x=[sel*100],y=[selected_stress],mode="markers",name="Selected strain",marker=dict(size=12,symbol="diamond"))); f.add_vline(x=ey*100,line_dash="dash",annotation_text="Estimated yield strain"); f.update_layout(title="Engineering stress–strain curve (idealized)",xaxis_title="Engineering strain (%)",yaxis_title="Engineering stress (MPa)")
    st.plotly_chart(chart_layout(f,420),use_container_width=True)
    df=pd.DataFrame({"engineering_strain_fraction":strain,"engineering_strain_pct":strain*100,"illustrative_stress_MPa":stress})
    downloads("materials_stress_strain",df,"Materials Stress Strain Report",[f"Young's modulus: {E:.3f} GPa",f"Yield strength: {ys:.3f} MPa",f"Ultimate strength input: {uts:.3f} MPa",f"Estimated yield strain: {ey*100:.5f}%",f"Selected strain: {sel*100:.4f}%",f"Illustrative selected stress: {selected_stress:.3f} MPa","Curve is a simplified teaching approximation, not experimental material data or a constitutive law."])
    st.warning("The post-yield curve is an illustrative interpolation, not a validated material model. Use certified material data for engineering design.")

def tutor_module():
    page_header("🤖 AI Engineering Tutor","Existing online Groq chatbot preserved. Configure GROQ_API_KEY in Streamlit Cloud → App settings → Secrets.")
    question=st.text_area("Your engineering question",placeholder="e.g., Explain Hooke's law and show a worked example.",height=130,key="tutor_question")
    if st.button("Ask AI tutor",type="primary",use_container_width=True):
        if not question.strip(): st.warning("Enter a question first.")
        else:
            try:
                key=st.secrets["GROQ_API_KEY"]
                response=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json={"model":"openai/gpt-oss-120b","messages":[{"role":"system","content":"You are a careful mechanical engineering tutor. Explain clearly, show equations and units, state assumptions, and warn when results require validation against a trusted engineering standard. Do not claim a preliminary model certifies a real design."},{"role":"user","content":question}],"temperature":0.3},timeout=60)
                response.raise_for_status(); st.session_state.chat_answer=response.json()["choices"][0]["message"]["content"]
            except KeyError: st.error("GROQ_API_KEY is missing from Streamlit Secrets. Add it in the app's Secrets settings; never paste the key into this code.")
            except requests.HTTPError: st.error(f"Groq returned HTTP {response.status_code}. Check provider/model availability and try again.")
            except requests.RequestException: st.error("Could not connect to Groq. Check internet connectivity and try again.")
            except Exception: st.error("The AI response could not be processed. Please try again.")
    if st.session_state.chat_answer: st.markdown("### Answer"); st.markdown(st.session_state.chat_answer)
    st.caption("This module uses the configured online API. It is not a local model; usage is subject to provider limits and availability.")

# Sidebar navigation: exactly one workspace is rendered at a time.
with st.sidebar:
    st.markdown("# ⚙️ MechLab Studio")
    st.caption("Mechanical engineering workbench")
    choices=["Home"]+list(MODULES.keys())
    current=st.session_state.active_module
    if current not in choices: current="Home"
    selected=st.radio("Navigation",choices,index=choices.index(current),format_func=lambda x: ("🏠  Home" if x=="Home" else f"{MODULES[x][0]}  {x}"),key="nav_radio")
    if selected != st.session_state.active_module: st.session_state.active_module=selected; st.rerun()
    st.divider(); st.caption("Built with Python · Streamlit · Plotly")

if st.session_state.active_module=="Home":
    st.markdown(f'<div class="hero"><h1>MechLab Studio</h1><p>One engineering module at a time. Calculate, simulate, inspect results, and export your readings from the module workspace.</p></div>',unsafe_allow_html=True)
    st.markdown("### Choose a workspace")
    st.write("Select a module below. Only that module's workspace opens; its calculations, graphs, simulation and downloads stay together on that page.")
    names=list(MODULES.keys())
    for start in range(0,len(names),2):
        cols=st.columns(2,gap="large")
        for col,name in zip(cols,names[start:start+2]):
            emoji,desc=MODULES[name]
            with col:
                st.markdown(f'<div class="module-card"><h3>{emoji} {name}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
                if st.button(f"Open {name} →",key=f"open_{name}",use_container_width=True): st.session_state.active_module=name; st.rerun()
    st.divider(); st.markdown("### Project notes")
    c1,c2,c3=st.columns(3); c1.metric("Workspaces","6","One active page at a time"); c2.metric("Export formats","CSV + PDF","Where applicable in each module"); c3.metric("AI connection","Groq API","Online; key stored in Secrets")
    st.caption("Engineering results are educational preliminary estimates. Validate against authoritative references and applicable standards before real-world use.")
elif st.session_state.active_module=="Spring Design": spring_module()
elif st.session_state.active_module=="Gear & Machine Design": gear_module()
elif st.session_state.active_module=="Thermal & Welding": thermal_module()
elif st.session_state.active_module=="Robotics & Kinematics": robotics_module()
elif st.session_state.active_module=="Materials & Stress–Strain": materials_module()
elif st.session_state.active_module=="AI Engineering Tutor": tutor_module()

