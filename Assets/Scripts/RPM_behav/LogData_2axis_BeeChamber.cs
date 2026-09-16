using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Globalization;

public class LogData_2axis_BeeChamber : MonoBehaviour
{
    public uint amount_of_probes = 0;
    public List<GameObject> probes = new List<GameObject>();
    string filePath;
    StreamWriter writer;
    // for data on the simulation
    public button_press_stable StartButton;
    public input_field_grabber InputField_RotFrameSpeed;
    public input_field_grabber InputField_BeeChamberSpeed;
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
    void FixedUpdate()
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
                string control = string.Format("{0:0.00}_{1:0.00}", InputField_RotFrameSpeed.input_float_val, InputField_BeeChamberSpeed.input_float_val);
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
                string header_str = "Time,OuterFrameSpeed,BeeChamberSpeed,OuterFrameAng,BeeChamberAng,BeeChamb_X,BeeChamb_Y,BeeChamb_Z"; //must end with a space
                string probe_id;
                foreach (GameObject probe in probes)
                {
                    probe_id = probe.GetComponent<Probe_positioning>().x.ToString() + "|" + probe.GetComponent<Probe_positioning>().y.ToString() + "|" + probe.GetComponent<Probe_positioning>().z.ToString();
                    header_str += "," + probe_id + "_X," + probe_id + "_Y," + probe_id + "_Z "; //must end with a space
                }
                writer.WriteLine(header_str);
            }

            ////////////////////////////////////////////////
            /// on each update 
            /////////////////////////////////////////////////////////

            float time = Time.time;
            // getting the current speeds
            float OuterFrameSpeed = InputField_RotFrameSpeed.input_float_val*6;
            float BeeChamberSpeed = InputField_BeeChamberSpeed.input_float_val*6;

            // writing data to file
            // time
            string line = time.ToString() + ",";
            // frame speeds
            line += OuterFrameSpeed.ToString() + "," + BeeChamberSpeed.ToString() + ",";
            // frame angles
            float OuterFrameAng = this.transform.parent.localEulerAngles.z;
            float BeeChamberAng = this.transform.localEulerAngles.y;
            line += OuterFrameAng.ToString() + "," + BeeChamberAng.ToString() + ",";
            // BeeChamber rotation vector
            Vector3 BeeChamberRot = this.GetComponent<Gravity_to_local>().local_grav_vector3;
            line += BeeChamberRot.x.ToString() + "," + BeeChamberRot.y.ToString() + "," + BeeChamberRot.z.ToString() + ",";
            // probe rotation vectors
            foreach (GameObject probe in probes)
            {
                Vector3 BeeChamb_Center = this.GetComponent<Transform>().position;
                Vector3 probe_loc = probe.GetComponent<Transform>().position;
                Vector3 probe_rot = probe_loc - BeeChamb_Center;    //normalizing the vector to local position
                line += probe_rot.x.ToString() + "," + probe_rot.y.ToString() + "," + probe_rot.z.ToString() + ",";
            }
            writer.WriteLine(line);
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
