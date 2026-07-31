using UnityEngine;

[ExecuteAlways]
public class RPM_snap : MonoBehaviour
{
    public GameObject ObjRotFrame;
    public GameObject ObjBeeChamber;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        ObjBeeChamber.transform.localPosition = Vector3.zero;

        Vector3 RotFrame_locPos = ObjRotFrame.transform.localPosition;
        RotFrame_locPos.x = 0f;
        RotFrame_locPos.z = 0f;
        ObjRotFrame.transform.localPosition = RotFrame_locPos;
    }
}
