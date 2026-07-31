using UnityEngine;

[ExecuteAlways]
public class Gravity_to_local : MonoBehaviour
{
    public Vector3 gravity_magnitude = new Vector3(0f,-9.81f,0f);
    public Matrix4x4 transform_mat;
    public Vector3 local_grav_vector3;
    public float checkLocalMagnitudeCalc;
    Vector4 grav_v4;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        // transform mat into rotation-like matrix
        transform_mat = transform.worldToLocalMatrix;
        transform_mat.SetRow(3, new Vector4(0f,0f,0f,1f));
        transform_mat.SetColumn(3, new Vector4(0f,0f,0f,1f));

        // create a Vector4 from the gravity Vector3 (w=0 for direction vector)
        grav_v4 = new Vector4(gravity_magnitude.x, gravity_magnitude.y, gravity_magnitude.z, 0f);
        Vector4 local_v4 = transform_mat * grav_v4;
        local_grav_vector3 = new Vector3(local_v4.x, local_v4.y, local_v4.z);

        //check local grav magnitude
        checkLocalMagnitudeCalc = local_grav_vector3.magnitude;
    }
}
