using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Globalization;

public class RPM3_log_data : MonoBehaviour
{
    // for timing freq
    public float data_write_frequency_Hz = 100.0f;  //[s]
    float time_passed = 0.0f;
    // Probe detection check
    public uint amount_of_probes = 0;
    public List<GameObject> probes = new List<GameObject>();
    string filePath;
    StreamWriter writer;
    // for data on the simulation
    public button_press_stable StartButton;
    public input_field_grabber InputField_OuterSpeed;
    public input_field_grabber InputField_IntermediateSpeed;
    public input_field_grabber InputField_InnerSpeed;
    bool isMoving = false;

    public List<GameObject> GetAllProbes()
    {
        List<GameObject> probes = new List<GameObject>();
        foreach (Transform child in transform){
            if(child.name != "default")
            {
                probes.Add(child.gameObject);
            }
        }
        return probes;
    }
    
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        // setting the culture to invariant to avoid problems with decimal separator
        CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;

        // getting probes
        amount_of_probes = (uint)this.transform.childCount-1;
        Debug.Log("Amount of Probes of BeeChamber: "+amount_of_probes);
        probes = GetAllProbes();
    }

    void OnDestroy()
    {
        if (writer != null)
        {
            writer.Close();
            writer = null;
            Debug.Log("Data logged to: " + filePath);
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (StartButton.isPressed)
        {

            if (!isMoving)
            {
                isMoving = true;
                Debug.Log("Started logging data");
                // creating the file
                string folder = Application.persistentDataPath;
                string baseName = "log";
                string extension = ".csv";
                string control = string.Format("{0:0.00}_{1:0.00}_{2:0.00}", 
                    InputField_OuterSpeed.input_float_val,
                    InputField_IntermediateSpeed.input_float_val,
                    InputField_InnerSpeed.input_float_val
                    );
                int fileIndex = 0;
                while (true)
                {
                    string fileName = baseName + fileIndex + "_" + control + extension;
                    filePath = Path.Combine(folder, fileName);
                    if (File.Exists(filePath))
                    {
                        fileIndex++;
                    } else
                    {
                        writer = new StreamWriter(filePath, false);
                        break;
                    }
                }

                //creating the header of the file   
                string header_str = "Time[s],OuterFrameSpeed[deg/s],IntermediateFrameSpeed[deg/s],InnerFrameSpeed[deg/s],OuterFrameAng[deg],IntermediateFrameAng[deg],InnerFrameAng[deg],BeeChamb_XYZ[m]"; //must end with a space
                string probe_id;
                foreach (GameObject probe in probes)
                {
                    probe_id = probe.GetComponent<Probe_positioning>().x.ToString() + "|" + probe.GetComponent<Probe_positioning>().y.ToString() + "|" + probe.GetComponent<Probe_positioning>().z.ToString();
                    header_str += "," + probe_id + "_pos," + probe_id + "_vel," + probe_id + "_acc"; //must end with a space
                }
                writer.WriteLine(header_str);

                time_passed = 0.0f;
            }

            time_passed += Time.deltaTime;
            if (time_passed >= 1/data_write_frequency_Hz)
            {
                time_passed = 0.0f;
                ////////////////////////////////////////////////
                /// on each update 
                /////////////////////////////////////////////////////////

                float time = Time.time;
                // getting the current speeds
                float OuterSpeed = InputField_OuterSpeed.input_float_val*6;
                float IntermediateSpeed = InputField_IntermediateSpeed.input_float_val*6;
                float InnerSpeed = InputField_InnerSpeed.input_float_val*6;

                // writing data to file
                // time
                string line = time.ToString() + ",";
                // frame speeds
                line += OuterSpeed.ToString() + "," 
                    + IntermediateSpeed.ToString() + ","
                    + InnerSpeed.ToString() + ",";
                // frame angles
                float OuterAng = this.transform.parent.localEulerAngles.z;
                float IntermediateAng = this.transform.localEulerAngles.y;
                float InnerAng = this.transform.localEulerAngles.x;
                line += OuterAng.ToString() + "," + IntermediateAng.ToString() + "," + InnerAng.ToString() + ",";
                // BeeChamber rotation vector
                Vector3 BeeChamberRot = this.GetComponent<Gravity_to_local>().local_grav_vector3;
                line += BeeChamberRot.x.ToString() + "|" + BeeChamberRot.y.ToString() + "|" + BeeChamberRot.z.ToString();
                // probe rotation vectors
                foreach (GameObject probe in probes)
                {
                    Vector3 BeeChamb_Center = this.GetComponent<Transform>().position;
                    Vector3 probe_loc = probe.GetComponent<Transform>().position;
                    Vector3 probe_rot = probe_loc - BeeChamb_Center;    //normalizing the vector to local position
                    //position
                    line += "," + string.Format("{0:F9}|{1:F9}|{2:F9}", probe_rot.x, probe_rot.y, probe_rot.z) ;
                    //line += probe_rot.x.ToString() + "," + probe_rot.y.ToString() + "," + probe_rot.z.ToString() + ",";
                    line += "," + string.Format("{0:F9}|{1:F9}|{2:F9}", probe.GetComponent<Rigidbody>().linearVelocity.x, probe.GetComponent<Rigidbody>().linearVelocity.y, probe.GetComponent<Rigidbody>().linearVelocity.z);
                    line += "," + string.Format("{0:F9}|{1:F9}|{2:F9}", probe.GetComponent<calc_rot_acc_vel>().acc_v3.x, probe.GetComponent<calc_rot_acc_vel>().acc_v3.y, probe.GetComponent<calc_rot_acc_vel>().acc_v3.z);
                }
                writer.WriteLine(line);
            }
        }
        else
        {
            if (writer != null)
            {
                writer.Close();
                writer = null;
                Debug.Log("Data logged to: " + filePath);
            }
            isMoving = false;
        }
    }
}
