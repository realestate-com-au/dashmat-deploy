import React, {Component, PropTypes} from 'react';
import WidgetBox from '/modules/dashmat.core_modules.components/WidgetBox.jsx';
import styles from './Reviews.css'

export class ReviewsModule extends Component {
  format_numbers() {
    var numbers = this.props.data.total_num_ratings + " Ratings "
    if (this.props.data.total_num_reviews != null) {
      numbers = numbers + " and " + this.props.data.total_num_reviews + " reviews"
    }
    return numbers;
  }

  render() {
    return (
      <WidgetBox {...this.props}>
        <div style={{padding: "5px"}}>
          <h3>{this.props.title} - {this.props.data.lable}</h3>
          <h4 style={{"text-align": "center"}}>{this.format_numbers()}</h4>
          <table className={styles.pretty}>
            <thead>
              <tr>
                <th>#stars</th>
                <th>Count</th>
              </tr>
            </thead>
            <tbody>
              {this.props.data.rating_list.map((v, i) =>
                <tr key={i}>
                  <td>{v[0]}</td>
                  <td>{v[1]}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </WidgetBox>
    )
  }
}

ReviewsModule.propTypes = {
  ...WidgetBox.propTypes,

  data: PropTypes.shape({
    label: PropTypes.string,
    total_num_ratings: PropTypes.number,
    total_num_reviews: PropTypes.number,

    rating_list: PropTypes.array,
  }),
  title: PropTypes.string,
};

