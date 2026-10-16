using UnityEngine;

[ExecuteAlways]
public class RPM3_snap : MonoBehaviour
{
    public GameObject ObjOuterFrame;
    public GameObject ObjIntermediateFrame;
    public GameObject ObjInnerFrame;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        ObjInnerFrame.transform.localPosition = Vector3.zero;
        ObjIntermediateFrame.transform.localPosition = Vector3.zero;
        ObjOuterFrame.transform.localPosition = Vector3.zero;
    }
}
