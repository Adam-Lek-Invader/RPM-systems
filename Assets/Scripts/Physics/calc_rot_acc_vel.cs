using UnityEngine;

public class calc_rot_acc_vel : MonoBehaviour
{
    //0 - newest, 2 - oldest
    [Header("Vectors [m/s], [m/s^2]")]
    public Vector3 acc_v3 = Vector3.zero;
    public Vector3 vel0_v3, vel1_v3 = Vector3.zero;
    public Vector3 pos0_v3, pos1_v3= Vector3.zero;
    [Header("Magnitudes [m/s], [m/s^2]")]
    public float last_deltaTime = 0f;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    public float acc_mag, vel_mag, calc_acc_mag = 0f;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        // position update
        pos1_v3 = pos0_v3;
        pos0_v3 = GetComponent<Transform>().position;

        // velocity update
        vel1_v3 = vel0_v3;
        vel0_v3 = (pos0_v3 - pos1_v3)/Time.deltaTime;

        //acceleration update
        acc_v3 = 2*(vel0_v3 - vel1_v3)/(Time.deltaTime+last_deltaTime);
        last_deltaTime = Time.deltaTime;

        //magnitudes updates
        acc_mag = acc_v3.magnitude;
        vel_mag = vel0_v3.magnitude;
        calc_acc_mag = vel_mag*vel_mag/GetComponent<Transform>().localPosition.magnitude;
    }
}
