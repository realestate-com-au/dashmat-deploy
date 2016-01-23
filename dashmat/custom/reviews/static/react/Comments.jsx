import React, {Component, PropTypes} from 'react';
import styles from '/modules/dashmat.server/Dashboard.css';

export class CommentsModule extends Component {
  render() {
    return (
      <flexcontainer>
        {this.props.data.nice_comments.map((c, i) =>
          <div key={i} className={styles.text_widget}>
            <p>{c}</p>
          </div>
        )}
      </flexcontainer>
    )
  }
}

CommentsModule.propTypes = {
  data: PropTypes.shape({
    nice_comments: PropTypes.array
  }),
  title: PropTypes.string,
};

